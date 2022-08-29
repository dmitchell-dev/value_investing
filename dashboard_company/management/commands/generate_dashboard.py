from django.core.management.base import BaseCommand
from ancillary_info.models import Companies
from calculated_stats.models import CalculatedStats
from financial_reports.models import FinancialReports
from share_prices.models import SharePrices
from dashboard_company.models import DashboardCompany
import pandas as pd
import numpy as np


class Command(BaseCommand):
    help = "Generate dashboard data"

    def handle(self, *args, **kwargs):

        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_columns", None)

        num_rows_created = 0
        num_rows_updated = 0

        # Companies
        df_companies = pd.DataFrame(list(Companies.objects.get_companies_joined()))

        df_companies.index = df_companies["tidm"]

        # Financial Data
        reporting_qs = FinancialReports.objects.raw(
            """SELECT reporting_data.id, tidm, company_name, param_name, time_stamp, value
                FROM reporting_data
                LEFT JOIN companies ON companies.id = reporting_data.company_id
                LEFT JOIN params ON params.id = reporting_data.parameter_id
                RIGHT JOIN (
                    SELECT MAX(time_stamp) AS time_stamp, company_id, parameter_id
                    FROM reporting_data
                    GROUP BY company_id, parameter_id)
                    subTable USING (parameter_id, company_id, time_stamp);"""
        )

        qs_list = []
        for row in reporting_qs:
            qs_list.append(
                [row.tidm, row.company_name, row.time_stamp, row.param_name, row.value]
            )

        df_reporting = pd.DataFrame(qs_list)
        df_reporting = df_reporting.rename(
            columns={
                0: "tidm",
                1: "company_name",
                2: "time_stamp",
                3: "param_name",
                4: "value",
            }
        )

        df_reporting = df_reporting.drop_duplicates(
            subset=["time_stamp", "company_name", "param_name"], keep="last"
        )

        df_financial_latest_date = df_reporting.groupby(['tidm'], sort=False)['time_stamp'].max().to_frame()
        df_financial_latest_date = df_financial_latest_date.rename(columns={"time_stamp": "financial_latest_date"}, errors="raise")

        df_reporting_pivot = df_reporting.pivot(
            columns="param_name",
            index="tidm",
            values="value",
        )

        # Calculated Stats
        calc_stats_qs = CalculatedStats.objects.raw(
            """SELECT calculated_data.id, tidm, company_name, param_name, time_stamp, value
                FROM calculated_data
                LEFT JOIN companies ON companies.id = calculated_data.company_id
                LEFT JOIN params ON params.id = calculated_data.parameter_id
                RIGHT JOIN (
                    SELECT MAX(time_stamp) AS time_stamp, company_id, parameter_id
                    FROM calculated_data
                    GROUP BY company_id, parameter_id)
                    subTable USING (parameter_id, company_id, time_stamp);"""
        )

        qs_list = []
        for row in calc_stats_qs:
            qs_list.append(
                [row.tidm, row.company_name, row.time_stamp, row.param_name, row.value]
            )

        df_calc_latest = pd.DataFrame(qs_list)
        df_calc_latest = df_calc_latest.rename(
            columns={
                0: "tidm",
                1: "company_name",
                2: "time_stamp",
                3: "param_name",
                4: "value",
            }
        )

        df_calc_latest_pivot = df_calc_latest.pivot(
            columns="param_name",
            index="tidm",
            values="value",
        )

        # Share Price Data
        share_qs = SharePrices.objects.raw(
            """SELECT share_price.id, tidm, company_name, time_stamp, value_adjusted
                FROM share_price
                LEFT JOIN companies ON companies.id = share_price.company_id
                RIGHT JOIN (
                    SELECT MAX(time_stamp) AS time_stamp, company_id
                    FROM share_price
                    GROUP BY company_id)
                    subTable USING (company_id, time_stamp);"""
        )

        qs_list = []
        for row in share_qs:
            qs_list.append(
                [row.tidm, row.company_name, row.time_stamp, row.value_adjusted]
            )

        df_share_latest = pd.DataFrame(qs_list)

        df_share_latest = df_share_latest.rename(
            columns={
                0: "tidm",
                1: "company_name",
                2: "share_latest_date",
                3: "value",
            }
        )

        df_share_latest = df_share_latest.drop(["company_name", "value"], axis=1)
        df_share_latest = df_share_latest.set_index("tidm")

        # Join dataframes
        df_merged = pd.merge(
            df_companies, df_calc_latest_pivot, left_index=True, right_index=True
        )

        df_merged = pd.merge(
            df_merged, df_reporting_pivot, left_index=True, right_index=True
        )

        df_merged = pd.merge(
            df_merged, df_share_latest, left_index=True, right_index=True
        )

        df_merged = pd.merge(
            df_merged, df_financial_latest_date, left_index=True, right_index=True
        )

        # Replace NaN for mySQL compatability
        df_merged = df_merged.replace(["NaN", "nan", "None"], np.nan)
        df_merged = df_merged.astype(object).where(pd.notnull(df_merged), None)

        # Split ready for create or update
        [df_create, df_update] = self._create_update_split(df_merged)

        # Create new companies
        if not df_create.empty:
            num_rows_created = self._create_rows(df_create)
            print(f"Dashboard Create Complete: {num_rows_created} rows updated")

        # Update existing companies
        if not df_update.empty:
            num_rows_updated = self._update_rows(df_update)
            print(f"Dashboard Update Complete: {num_rows_updated} rows updated")

        return f"Created: {str(num_rows_created)}, Updated: {str(num_rows_updated)}"

    def _create_update_split(self, new_df):
        existing_df = pd.DataFrame(list(DashboardCompany.objects.get_dash_joined()))

        if not existing_df.empty:
            split_idx = np.where(
                new_df["tidm"].isin(existing_df["tidm"]), "existing", "new"
            )
            df_existing = new_df[split_idx == "existing"]
            df_new = new_df[split_idx == "new"]
        else:
            df_new = new_df
            df_existing = pd.DataFrame()

        return df_new, df_existing

    def _create_rows(self, df_create):

        # Save to database
        reports = [
            DashboardCompany(
                company=Companies.objects.get(id=row["id"]),
                tidm=row["tidm"],
                company_name=row["company_name"],
                company_summary=row["company_summary"],
                share_listing=row["exchange__value"],
                company_type=row["comp_type__value"],
                industry_name=row["industry__value"],
                revenue=float(row["Total Revenue"]),
                earnings=float(row["Reported EPS"]),
                dividends=float(row["Dividends Per Share"]),
                capital_expenditure=float(row["Capital Expenditures"]),
                net_income=float(row["Net Income"]),
                total_equity=float(row["Total Equity"]),
                share_price=float(row["Share Price"]),
                debt_to_equity=float(row["Debt to Equity (D/E)"]),
                current_ratio=float(row["Current Ratio"]),
                return_on_equity=float(row["Return on Equity (ROE)"]),
                equity_per_share=float(row["Equity (Book Value) Per Share"]),
                price_to_earnings=float(row["Price to Earnings (P/E)"]),
                price_to_equity=float(row["Price to Book Value (Equity)"]),
                earnings_yield=float(row["Earnings Yield"]),
                annual_yield_return=float(row["Annual Yield (Return)"]),
                fcf=float(row["Free Cash Flow"]),
                dividend_cover=float(row["Dividend Cover"]),
                capital_employed=float(row["Capital Employed"]),
                roce=float(row["Return on Capital Employed (ROCE)"]),
                dcf_intrinsic_value=float(row["Intrinsic Value"]),
                margin_safety=float(row["Margin of Safety"]),
                latest_margin_of_safety=float(row["Latest Margin of Safety"]),
                estimated_growth_rate=float(row["Estimated Growth Rate"]),
                estimated_discount_rate=float(row["Estimated Discount Rate"]),
                estimated_long_term_growth_rate=float(
                    row["Estimated Long Term Growth Rate"]
                ),
                pick_source=row["company_source__value"],
                exchange_country=row["country__value"],
                currency_symbol=row["currency__symbol"],
                latest_financial_date=row["financial_latest_date"],
                latest_share_price_date=row["share_latest_date"],
                market_cap=float(row["Market Capitalisation"]),
            )
            for i, row in df_create.iterrows()
        ]
        list_of_objects = DashboardCompany.objects.bulk_create(reports)

        total_rows_added = len(list_of_objects)

        return total_rows_added

    def _update_rows(self, df_update):

        companies = list(DashboardCompany.objects.all())
        num_companies = len(companies)
        company_num = 0
        total_rows = 0

        param_dict = {
            "industry_name": "industry__value",
            "revenue": "Total Revenue",
            "earnings": "Reported EPS",
            "dividends": "Dividends Per Share",
            "capital_expenditure": "Capital Expenditures",
            "net_income": "Net Income",
            "total_equity": "Total Equity",
            "share_price": "Share Price",
            "debt_to_equity": "Debt to Equity (D/E)",
            "current_ratio": "Current Ratio",
            "return_on_equity": "Return on Equity (ROE)",
            "equity_per_share": "Equity (Book Value) Per Share",
            "price_to_earnings": "Price to Earnings (P/E)",
            "price_to_equity": "Price to Book Value (Equity)",
            "earnings_yield": "Earnings Yield",
            "annual_yield_return": "Annual Yield (Return)",
            "fcf": "Free Cash Flow",
            "dividend_cover": "Dividend Cover",
            "capital_employed": "Capital Employed",
            "roce": "Return on Capital Employed (ROCE)",
            "dcf_intrinsic_value": "Intrinsic Value",
            "margin_safety": "Margin of Safety",
            "latest_margin_of_safety": "Latest Margin of Safety",
            "estimated_growth_rate": "Estimated Growth Rate",
            "estimated_discount_rate": "Estimated Discount Rate",
            "estimated_long_term_growth_rate": "Estimated Long Term Growth Rate",
            "market_cap": "Market Capitalisation",
            "pick_source": "company_source__value",
            "exchange_country": "country__value",
            "currency_symbol": "currency__symbol",
            "latest_share_price_date": "share_latest_date",
            "latest_financial_date": "financial_latest_date",
        }

        for index, company in enumerate(companies):

            # For each company, get the associated row in df
            df_update = df_update.reset_index(drop=True)
            cur_row = df_update[df_update["tidm"] == company.tidm].index[0]

            company_num = company_num + 1
            print(f"Company {company_num} of {num_companies}, {company.tidm}")

            if cur_row:
                companies[index].industry_name = df_update.loc[
                    df_update.index[cur_row], "industry__value"
                ]

                companies[index].revenue = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Total Revenue"]
                )

                companies[index].earnings = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Reported EPS"]
                )

                companies[index].dividends = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Dividends Per Share"]
                )

                companies[index].capital_expenditure = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Capital Expenditures"]
                )

                companies[index].net_income = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Net Income"]
                )

                companies[index].total_equity = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Total Equity"]
                )

                companies[index].share_price = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Share Price"]
                )

                companies[index].debt_to_equity = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Debt to Equity (D/E)"]
                )

                companies[index].current_ratio = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Current Ratio"]
                )

                companies[index].return_on_equity = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Return on Equity (ROE)"]
                )

                companies[index].equity_per_share = self._convert_float(
                    df_update.loc[
                        df_update.index[cur_row], "Equity (Book Value) Per Share"
                    ]
                )

                companies[index].price_to_earnings = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Price to Earnings (P/E)"]
                )

                companies[index].price_to_equity = self._convert_float(
                    df_update.loc[
                        df_update.index[cur_row], "Price to Book Value (Equity)"
                    ]
                )

                companies[index].earnings_yield = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Earnings Yield"]
                )

                companies[index].annual_yield_return = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Annual Yield (Return)"]
                )

                companies[index].fcf = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Free Cash Flow"]
                )

                companies[index].dividend_cover = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Dividend Cover"]
                )

                companies[index].capital_employed = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Capital Employed"]
                )

                companies[index].roce = self._convert_float(
                    df_update.loc[
                        df_update.index[cur_row], "Return on Capital Employed (ROCE)"
                    ]
                )

                companies[index].dcf_intrinsic_value = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Intrinsic Value"]
                )

                companies[index].margin_safety = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Margin of Safety"]
                )

                companies[index].latest_margin_of_safety = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Latest Margin of Safety"]
                )

                companies[index].estimated_growth_rate = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Estimated Growth Rate"]
                )

                companies[index].estimated_discount_rate = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Estimated Discount Rate"]
                )

                companies[index].estimated_long_term_growth_rate = self._convert_float(
                    df_update.loc[
                        df_update.index[cur_row], "Estimated Long Term Growth Rate"
                    ]
                )

                companies[index].pick_source = df_update.loc[
                    df_update.index[cur_row], "company_source__value"
                ]

                companies[index].exchange_country = df_update.loc[
                    df_update.index[cur_row], "country__value"
                ]

                companies[index].currency_symbol = df_update.loc[
                    df_update.index[cur_row], "currency__symbol"
                ]

                companies[index].latest_financial_date = df_update.loc[
                    df_update.index[cur_row], "financial_latest_date"
                ]

                companies[index].latest_share_price_date = df_update.loc[
                    df_update.index[cur_row], "share_latest_date"
                ]

                companies[index].market_cap = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Market Capitalisation"]
                )

        print("Updating Dashboard Table")

        for key in param_dict:
            num_rows_updated = DashboardCompany.objects.bulk_update(companies, [key])
            total_rows = total_rows + num_rows_updated

        return total_rows

    def _convert_float(self, input):

        if pd.notnull(input):
            output = float(input)
        else:
            output = input

        return output
