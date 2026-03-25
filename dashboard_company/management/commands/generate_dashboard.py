from django.core.management.base import BaseCommand
from django.utils import timezone
from ancillary_info.models import Companies
from calculated_stats.models import CalculatedStats
from financial_reports.models import FinancialReports
from share_prices.models import SharePrices
from dashboard_company.models import DashboardCompany
from portfolio.models import Transactions, WishList, DecisionType

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
                3: "latest_share_price",
            }
        )

        df_share_latest = df_share_latest.drop(["company_name"], axis=1)
        df_share_latest = df_share_latest.set_index("tidm")

        # Look up dashboard decision type IDs by value (avoids hardcoding auto-assigned PKs)
        from ancillary_info.models import DecisionType as DT
        dt_no    = DT.objects.get_or_create(value="No")[0].id
        dt_watch = DT.objects.get_or_create(value="Watch")[0].id
        dt_hold  = DT.objects.get_or_create(value="Hold")[0].id
        dt_sold  = DT.objects.get_or_create(value="Sold")[0].id

        # Generate decision type column — default: No
        df_decision_type = pd.DataFrame(list(Companies.objects.get_companies_tidm()))
        df_decision_type['decision_type'] = dt_no
        df_decision_type = df_decision_type.set_index("tidm")
        df_decision_type = df_decision_type.drop('id', axis=1)

        # Wish List
        df_wish_list = pd.DataFrame(list(WishList.objects.get_table_joined()))
        df_decision_type['decision_type'] = np.where(
            df_decision_type.index.isin(df_wish_list.company__tidm),
            dt_watch,
            df_decision_type.decision_type,
        )

        # Transaction list (Holding / Sold)
        df_transaction_list = pd.DataFrame(list(Transactions.objects.get_latest_transactions()))
        df_transaction_list = df_transaction_list.rename(columns={"company__tidm": "tidm"})
        df_transaction_list = df_transaction_list.set_index("tidm")
        df_transaction_list['decision_type'] = dt_no
        df_transaction_list['decision_type'] = df_transaction_list['decision_type'].mask(df_transaction_list['num_stock_balance'] == 0, dt_sold)
        df_transaction_list['decision_type'] = df_transaction_list['decision_type'].mask(df_transaction_list['num_stock_balance'] != 0, dt_hold)

        # Merge back into decision type df — update() only overwrites rows that
        # exist in df_transaction_list, leaving all other rows unchanged.
        if not df_transaction_list.empty:
            df_decision_type.update(df_transaction_list[['decision_type']])
        df_decision_type['decision_type'] = df_decision_type['decision_type'].astype(int)

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

        df_merged = pd.merge(
            df_merged, df_decision_type, left_index=True, right_index=True
        )

        # Replace NaN for mySQL compatability
        df_merged = df_merged.astype(str)
        df_merged = df_merged.replace(["NaN", "nan", "None"], np.nan)

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

        # Issue with adding new companies
        # Is the new company in the update df?
        return df_new, df_existing

    def _create_rows(self, df_create):

        # Save to database
        reports = [
            DashboardCompany(
                company=Companies.objects.get(id=row["id"]),
                decision_type=DecisionType.objects.get(id=row["decision_type"]),
                tidm=row["tidm"],
                company_name=row["company_name"],
                company_summary=row["company_summary"],
                share_listing=row["exchange__value"],
                company_type=row["comp_type__value"],
                industry_name=row["industry__value"],
                revenue=self._convert_float(row.get("Total Revenue")),
                earnings=self._convert_float(row.get("EPS")),
                dividends=self._convert_float(row.get("Dividends Per Share")),
                capital_expenditure=self._convert_float(row.get("Capital Expenditure")),
                net_income=self._convert_float(row.get("Net Income")),
                total_equity=self._convert_float(row.get("Total Equity")),
                share_price=self._convert_float(row.get("Share Price")),
                debt_to_equity=self._convert_float(row.get("Debt to Equity")),
                current_ratio=self._convert_float(row.get("Current Ratio")),
                return_on_equity=self._convert_float(row.get("Return on Equity")),
                equity_per_share=self._convert_float(row.get("Equity (Book Value) Per Share")),
                price_to_earnings=self._convert_float(row.get("Price to Earnings")),
                price_to_equity=self._convert_float(row.get("Price to Book Value (Equity)")),
                earnings_yield=self._convert_float(row.get("Earnings Yield")),
                annual_yield_return=self._convert_float(row.get("Annual Yield (Return)")),
                fcf=self._convert_float(row.get("Free Cash Flow")),
                dividend_cover=self._convert_float(row.get("Dividend Cover")),
                capital_employed=self._convert_float(row.get("Capital Employed")),
                roce=self._convert_float(row.get("ROCE")),
                dcf_intrinsic_value=self._convert_float(row.get("DCF Intrinsic Value")),
                margin_safety=self._convert_float(row.get("Margin of Safety")),
                latest_margin_of_safety=self._convert_float(row.get("Latest Margin of Safety")),
                estimated_growth_rate=self._convert_float(row.get("Estimated Growth Rate")),
                estimated_discount_rate=self._convert_float(row.get("Estimated Discount Rate")),
                estimated_long_term_growth_rate=self._convert_float(
                    row.get("Estimated Long Term Growth Rate")
                ),
                pick_source=row["company_source__value"],
                exchange_country=row["country__value"],
                currency_symbol=row["currency__symbol"],
                latest_financial_date=self._make_aware(row["financial_latest_date"]),
                latest_share_price_date=self._make_aware(row["share_latest_date"]),
                latest_share_price=row["latest_share_price"],
                market_cap=float(row["Market Capitalisation"]),
                net_margin=self._convert_float(row.get("Net Margin")),
                gross_margin=self._convert_float(row.get("Gross Margin")),
                operating_margin=self._convert_float(row.get("Operating Margin")),
                interest_coverage=self._convert_float(row.get("Interest Coverage")),
                dividend_payout_ratio=self._convert_float(row.get("Dividend Payout Ratio")),
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
            "decision_type": "decision_type",
            "company_summary": "company_summary",
            "industry_name": "industry__value",
            "revenue": "Total Revenue",
            "earnings": "EPS",
            "dividends": "Dividends Per Share",
            "capital_expenditure": "Capital Expenditure",
            "net_income": "Net Income",
            "total_equity": "Total Equity",
            "share_price": "Share Price",
            "debt_to_equity": "Debt to Equity",
            "current_ratio": "Current Ratio",
            "return_on_equity": "Return on Equity",
            "equity_per_share": "Equity (Book Value) Per Share",
            "price_to_earnings": "Price to Earnings",
            "price_to_equity": "Price to Book Value (Equity)",
            "earnings_yield": "Earnings Yield",
            "annual_yield_return": "Annual Yield (Return)",
            "fcf": "Free Cash Flow",
            "dividend_cover": "Dividend Cover",
            "capital_employed": "Capital Employed",
            "roce": "ROCE",
            "dcf_intrinsic_value": "DCF Intrinsic Value",
            "margin_safety": "Margin of Safety",
            "latest_margin_of_safety": "Latest Margin of Safety",
            "estimated_growth_rate": "Estimated Growth Rate",
            "estimated_discount_rate": "Estimated Discount Rate",
            "estimated_long_term_growth_rate": "Estimated Long Term Growth Rate",
            "market_cap": "Market Capitalisation",
            "net_margin": "Net Margin",
            "gross_margin": "Gross Margin",
            "operating_margin": "Operating Margin",
            "interest_coverage": "Interest Coverage",
            "dividend_payout_ratio": "Dividend Payout Ratio",
            "pick_source": "company_source__value",
            "exchange_country": "country__value",
            "currency_symbol": "currency__symbol",
            "latest_share_price_date": "share_latest_date",
            "latest_share_price": "latest_share_price",
            "latest_financial_date": "financial_latest_date",
        }

        for index, company in enumerate(companies):

            # If company is in the update list
            if df_update['tidm'].str.contains(company.tidm).any():

                # For each company, get the associated row in df
                df_update = df_update.reset_index(drop=True)

                # Issue with adding new companies
                # Is the new company in the update df?
                cur_row = df_update[df_update["tidm"] == company.tidm].index[0]

                company_num = company_num + 1
                print(f"Company {company_num} of {num_companies}, {company.tidm}")

                if cur_row:
                    companies[index].decision_type = DecisionType.objects.get(
                        id=df_update.loc[df_update.index[cur_row], "decision_type"]
                        )

                    companies[index].company_summary = df_update.loc[
                        df_update.index[cur_row], "company_summary"
                    ] or ""

                    companies[index].industry_name = df_update.loc[
                        df_update.index[cur_row], "industry__value"
                    ]

                    companies[index].revenue = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Total Revenue")
                    )

                    companies[index].earnings = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("EPS")
                    )

                    companies[index].dividends = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Dividends Per Share")
                    )

                    companies[index].capital_expenditure = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Capital Expenditure")
                    )

                    companies[index].net_income = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Net Income")
                    )

                    companies[index].total_equity = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Total Equity")
                    )

                    companies[index].share_price = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Share Price")
                    )

                    companies[index].debt_to_equity = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Debt to Equity")
                    )

                    companies[index].current_ratio = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Current Ratio")
                    )

                    companies[index].return_on_equity = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Return on Equity")
                    )

                    companies[index].equity_per_share = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Equity (Book Value) Per Share")
                    )

                    companies[index].price_to_earnings = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Price to Earnings")
                    )

                    companies[index].price_to_equity = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Price to Book Value (Equity)")
                    )

                    companies[index].earnings_yield = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Earnings Yield")
                    )

                    companies[index].annual_yield_return = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Annual Yield (Return)")
                    )

                    companies[index].fcf = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Free Cash Flow")
                    )

                    companies[index].dividend_cover = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Dividend Cover")
                    )

                    companies[index].capital_employed = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Capital Employed")
                    )

                    companies[index].roce = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("ROCE")
                    )

                    companies[index].dcf_intrinsic_value = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("DCF Intrinsic Value")
                    )

                    companies[index].margin_safety = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Margin of Safety")
                    )

                    companies[index].latest_margin_of_safety = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Latest Margin of Safety")
                    )

                    companies[index].estimated_growth_rate = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Estimated Growth Rate")
                    )

                    companies[index].estimated_discount_rate = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Estimated Discount Rate")
                    )

                    companies[index].estimated_long_term_growth_rate = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Estimated Long Term Growth Rate")
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

                    companies[index].latest_financial_date = self._make_aware(
                        df_update.loc[df_update.index[cur_row], "financial_latest_date"]
                    )

                    companies[index].latest_share_price_date = self._make_aware(
                        df_update.loc[df_update.index[cur_row], "share_latest_date"]
                    )

                    companies[index].latest_share_price = df_update.loc[
                        df_update.index[cur_row], "latest_share_price"
                    ]

                    companies[index].market_cap = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Market Capitalisation")
                    )

                    companies[index].net_margin = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Net Margin")
                    )

                    companies[index].gross_margin = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Gross Margin")
                    )

                    companies[index].operating_margin = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Operating Margin")
                    )

                    companies[index].interest_coverage = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Interest Coverage")
                    )

                    companies[index].dividend_payout_ratio = self._convert_float(
                        df_update.loc[df_update.index[cur_row]].get("Dividend Payout Ratio")
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

    def _make_aware(self, value):
        """Convert a naive date/datetime to a timezone-aware datetime, or return None."""
        if pd.isnull(value) if not isinstance(value, str) else value in ("NaN", "nan", "None", ""):
            return None
        try:
            dt = pd.Timestamp(value).to_pydatetime()
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt)
            return dt
        except Exception:
            return None
