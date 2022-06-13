from django.core.management.base import BaseCommand
from ancillary_info.models import Companies
from calculated_stats.models import CalculatedStats
from financial_reports.models import FinancialReports
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

        # Replace NaN for mySQL compatability
        df_merged = df_merged.replace([np.nan, "NaN", "nan", "None"], "-9999")

        df_merged = df_merged.drop("id", axis=1)

        # for col in df_merged.columns:
        #     print(col)

        # Save to database
        reports = [
            DashboardCompany(
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
                dividend_payment=row["Dividend Payout"],
                dividend_cover=float(row["Dividend Cover"]),
                capital_employed=float(row["Capital Employed"]),
                roce=float(row["Return on Capital Employed (ROCE)"]),
                dcf_intrinsic_value=float(row["Intrinsic Value"]),
                margin_safety=float(row["Margin of Safety"]),
                estimated_growth_rate=float(row["Estimated Growth Rate"]),
                estimated_discount_rate=float(row["Estimated Discount Rate"]),
                estimated_long_term_growth_rate=float(row["Estimated Long Term Growth Rate"]),
            )
            for i, row in df_merged.iterrows()
        ]
        DashboardCompany.objects.bulk_create(reports)

        print("Dashboard Complete")
