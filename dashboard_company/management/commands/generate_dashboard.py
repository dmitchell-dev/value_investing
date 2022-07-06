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

        # Companies
        df_companies = pd.DataFrame(
            list(Companies.objects.get_companies_joined())
            )

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
            qs_list.append([
                row.tidm,
                row.company_name,
                row.time_stamp,
                row.param_name,
                row.value
                ])

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

        financial_latest_date = df_reporting['time_stamp'].max()

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

        df_share_latest = df_share_latest.drop(['company_name', 'value'], axis=1)
        df_share_latest = df_share_latest.set_index('tidm')

        # Join dataframes
        df_merged = pd.merge(
            df_companies,
            df_calc_latest_pivot,
            left_index=True,
            right_index=True
        )

        df_merged = pd.merge(
            df_merged,
            df_reporting_pivot,
            left_index=True,
            right_index=True
        )

        df_merged = pd.merge(
            df_merged,
            df_share_latest,
            left_index=True,
            right_index=True
        )

        # Replace NaN for mySQL compatability
        df_merged = df_merged.replace([np.nan, "NaN", "nan", "None"], "-9999")

        # Split ready for create or update
        [df_create, df_update] = self._create_update_split(df_merged)

        # Create new companies
        if not df_create.empty:
            self._create_rows(df_create, financial_latest_date)

        # Update existing companies
        if not df_update.empty:
            self._update_rows(df_update, financial_latest_date)

        print("Dashboard Complete")

    def _create_update_split(self, new_df):
        existing_df = pd.DataFrame(
            list(DashboardCompany.objects.get_dash_joined())
            )

        if not existing_df.empty:
            test_index = np.where(new_df['tidm'].isin(existing_df['tidm']), 'existing', 'new')
            df_existing = new_df[test_index == 'existing']
            df_new = new_df[test_index == 'new']
        else:
            df_new = new_df
            df_existing = None

        return [df_new, df_existing]

    def _create_rows(self, df_create, financial_latest_date):

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
                estimated_growth_rate=float(row["Estimated Growth Rate"]),
                estimated_discount_rate=float(row["Estimated Discount Rate"]),
                estimated_long_term_growth_rate=float(row["Estimated Long Term Growth Rate"]),
                pick_source=row["company_source__value"],
                exchange_country=row["country__value"],
                currency_symbol=row["currency__value"],
                latest_financial_date=financial_latest_date,
                latest_share_price_date=row["share_latest_date"],
                market_cap=float(row["Market Capitalisation"]),
            )
            for i, row in df_create.iterrows()
        ]
        DashboardCompany.objects.bulk_create(reports)

    def _update_rows(self, df_update, financial_latest_date):

        update_cols = [
            'company',
            'revenue',
            'earnings',
            'dividends',
            'capital_expenditure',
            'net_income',
            'total_equity',
            'share_price',
            'debt_to_equity',
            'current_ratio',
            'return_on_equity',
            'equity_per_share',
            'price_to_earnings',
            'price_to_equity',
            'earnings_yield',
            'annual_yield_return',
            'fcf',
            'dividend_cover',
            'capital_employed',
            'roce',
            'dcf_intrinsic_value',
            'margin_safety',
            'estimated_growth_rate',
            'estimated_discount_rate',
            'estimated_long_term_growth_rate',
            'pick_source',
            'exchange_country',
            'currency_symbol',
            'latest_financial_date',
            'latest_share_price_date',
            'market_cap',
            ]

        companies = list(DashboardCompany.objects.all())
        for index, company in enumerate(companies):
            companies[index].industry_name = f"Updated Test {index}"
        DashboardCompany.objects.bulk_update(companies, ['industry_name'])
