from django.core.management.base import BaseCommand
from ancillary_info.models import Companies
from calculated_stats.models import CalculatedStats
from ranking_stats.models import RankingStats
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
        df_companies = pd.DataFrame(list(Companies.objects.get_companies_joined()))

        df_companies.index = df_companies["tidm"]

        # Financial Data
        reporting_qs = FinancialReports.objects.raw(
            """SELECT reporting_data.id, tidm, company_name, param_name, time_stamp, value
                FROM reporting_data
                LEFT JOIN companies ON companies.id = reporting_data.company_id
                LEFT JOIN parameters ON parameters.id = reporting_data.parameter_id
                RIGHT JOIN (
                    SELECT MAX(time_stamp) AS time_stamp, company_id, parameter_id
                    FROM reporting_data
                    GROUP BY company_id, parameter_id ORDER BY NULL)
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
                LEFT JOIN parameters ON parameters.id = calculated_data.parameter_id
                RIGHT JOIN (
                    SELECT MAX(time_stamp) AS time_stamp, company_id, parameter_id
                    FROM calculated_data
                    GROUP BY company_id, parameter_id ORDER BY NULL)
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

        # Ranking Stats
        rank_stats_qs = RankingStats.objects.raw(
            """SELECT ranking_data.id, tidm, company_name, param_name, time_stamp, value
                FROM ranking_data
                LEFT JOIN companies ON companies.id = ranking_data.company_id
                LEFT JOIN parameters ON parameters.id = ranking_data.parameter_id
                RIGHT JOIN (
                    SELECT MAX(time_stamp) AS time_stamp, company_id, parameter_id
                    FROM ranking_data
                    GROUP BY company_id, parameter_id ORDER BY NULL)
                    subTable USING (parameter_id, company_id, time_stamp);"""
        )

        qs_list = []
        for row in rank_stats_qs:
            qs_list.append(
                [row.tidm, row.company_name, row.time_stamp, row.param_name, row.value]
            )

        df_rank_latest = pd.DataFrame(qs_list)
        df_rank_latest = df_rank_latest.rename(
            columns={
                0: "tidm",
                1: "company_name",
                2: "time_stamp",
                3: "param_name",
                4: "value",
            }
        )

        df_rank_latest_pivot = df_rank_latest.pivot(
            columns="param_name",
            index="tidm",
            values="value",
        )

        # Join dataframes
        df_merged = pd.merge(
            df_companies, df_calc_latest_pivot, left_index=True, right_index=True
        )

        df_merged = pd.merge(
            df_merged, df_reporting_pivot, left_index=True, right_index=True
        )

        df_merged = pd.merge(
            df_merged, df_rank_latest_pivot, left_index=True, right_index=True
        )

        # Replace NaN for mySQL compatability
        df_merged = df_merged.replace([np.nan, "NaN", "nan", "None"], "-9999")

        df_merged = df_merged.drop("id", axis=1)

        for col in df_merged.columns:
            print(col)

        # Save to database
        reports = [
            DashboardCompany(
                tidm=row["tidm"],
                company_name=row["company_name"],
                company_summary=row["company_summary"],
                share_listing=row["market__share_listing"],
                company_type=row["comp_type__company_type"],
                industry_name=row["industry__industry_name"],
                turnover=float(row["Turnover"]),
                earnings=float(row["EPS rep. continuous"]),
                dividends=float(row["Dividend (announced) ps"]),
                total_borrowing=float(row["Total borrowing"]),
                shareholder_equity=float(row["Shareholders funds (NAV)"]),
                capital_expenditure=float(row["Capital expenditure"]),
                net_profit=float(row["Profit for financial year"]),
                total_equity=float(row["Total equity"]),
                depreciation_amortisation=float(row["Depreciation & amortisation"]),
                acquisitions=float(row["Acquisitions"]),
                avg_shares=float(row["Average shares (diluted)"]),
                share_price=float(row["Share Price"]),
                debt_to_equity=float(row["Debt to Equity (D/E)"]),
                current_ratio=float(row["Current Ratio"]),
                return_on_equity=float(row["Return on Equity (ROE)"]),
                equity_per_share=float(row["Equity (Book Value) Per Share"]),
                price_to_earnings=float(row["Price to Earnings (P/E)"]),
                price_to_equity=float(row["Price to Book Value (Equity)"]),
                annual_return=float(row["Annual Yield (Return)"]),
                fcf_growth_rate=float(row["Free cash flow (FCF)"]),
                fcf_ps=float(row["FCF ps"]),
                dividend_payment=row["Dividend Payment"],
                dividend_cover=float(row["Dividend Cover"]),
                revenue_growth=row["Revenue Growth"],
                eps_growth=row["EPS Growth"],
                dividend_growth=row["Dividend Growth"],
                growth_quality=float(row["Growth Quality"]),
                revenue_rowth_10=float(row["Revenue Growth (10 year)"]),
                earnings_growth_10=float(row["Earnings Growth (10 year)"]),
                dividend_growth_10=float(row["Dividend Growth (10 year)"]),
                overall_growth_10=float(row["Overall Growth (10 year)"]),
                growth_rate_10=float(row["Growth Rate (10 year)"]),
                capital_employed=float(row["Capital Employed"]),
                roce=float(row["ROCE"]),
                median_roce_10=float(row["Median ROCE (10 year)"]),
                debt_ratio=float(row["Debt Ratio"]),
                pe_10=float(row["PE10"]),
                dp_10=float(row["DP10"]),
                growth_rate_10_rank_value=float(
                    row["Growth Rate (10 year) Rank Value"]
                ),
                growth_quality_rank_value=float(row["Growth Quality Rank Value"]),
                median_roce_10_rank_value=float(
                    row["Median ROCE (10 year) Rank Value"]
                ),
                pe_10_rank_value=float(row["PE10 Rank Value"]),
                dp_10_rank_value=float(row["DP10 Rank Value"]),
                growth_rate_10_rank=float(row["Growth Rate (10 year) Rank"]),
                growth_quality_rank=float(row["Growth Quality Rank"]),
                median_roce_10_rank=float(row["Median ROCE (10 year) Rank"]),
                pe_10_rank=float(row["PE10 Rank"]),
                dp_10_rank=float(row["DP10 Rank"]),
                defensive_rank=float(row["Defensive Rank"]),
                dcf_intrinsic_value=float(row["DCF Intrinsic Value"]),
                estimated_growth_rate=float(row["Estimated Growth Rate"]),
                estimated_discount_rate=float(row["Estimated Discount Rate"]),
                estimated_long_term_growth_rate=float(
                    row["Estimated Long Term Growth Rate"]
                ),
            )
            for i, row in df_merged.iterrows()
        ]
        DashboardCompany.objects.bulk_create(reports)

        print("Dashboard Complete")
