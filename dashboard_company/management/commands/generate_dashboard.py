from django.core.management.base import BaseCommand
from ancillary_info.models import Companies
from calculated_stats.models import CalculatedStats
from ranking_stats.models import RankingStats
from dashboard_company.models import DashboardCompany
import pandas as pd
import numpy as np


class Command(BaseCommand):
    help = "Generate dashboard data"

    def handle(self, *args, **kwargs):

        # Companies
        df_companies = pd.DataFrame(
            list(Companies.objects.get_companies_joined())
            )

        df_companies.index = df_companies['tidm']

        # Calculated Stats
        calc_stats_qs = CalculatedStats.objects.raw(
            '''SELECT calculated_data.id, tidm, company_name, param_name, time_stamp, value
                FROM calculated_data
                LEFT JOIN companies ON companies.id = calculated_data.company_id
                LEFT JOIN parameters ON parameters.id = calculated_data.parameter_id
                RIGHT JOIN (
                    SELECT MAX(time_stamp) AS time_stamp, company_id, parameter_id
                    FROM calculated_data
                    GROUP BY company_id, parameter_id ORDER BY NULL)
                    subTable USING (parameter_id, company_id, time_stamp);''')

        qs_list = []
        for row in calc_stats_qs:
            qs_list.append([row.tidm, row.company_name, row.time_stamp, row.param_name, row.value])

        df_calc_latest = pd.DataFrame(qs_list)
        df_calc_latest = df_calc_latest.rename(columns={0: "tidm", 1: "company_name", 2: "time_stamp", 3: "param_name", 4:"value"})

        df_calc_latest_pivot = df_calc_latest.pivot(
            columns="param_name",
            index="tidm",
            values="value",
        )

        df_calc_latest_pivot = df_calc_latest_pivot.replace(["nan", "None"], "NaN")

        # Ranking Stats
        rank_stats_qs = RankingStats.objects.raw(
            '''SELECT ranking_data.id, tidm, company_name, param_name, time_stamp, value
                FROM ranking_data
                LEFT JOIN companies ON companies.id = ranking_data.company_id
                LEFT JOIN parameters ON parameters.id = ranking_data.parameter_id
                RIGHT JOIN (
                    SELECT MAX(time_stamp) AS time_stamp, company_id, parameter_id
                    FROM ranking_data
                    GROUP BY company_id, parameter_id ORDER BY NULL)
                    subTable USING (parameter_id, company_id, time_stamp);''')

        qs_list = []
        for row in rank_stats_qs:
            qs_list.append([
                row.tidm,
                row.company_name,
                row.time_stamp,
                row.param_name,
                row.value
                ])

        df_rank_latest = pd.DataFrame(qs_list)
        df_rank_latest = df_rank_latest.rename(columns={
            0: "tidm",
            1: "company_name",
            2: "time_stamp",
            3: "param_name",
            4: "value"
            })

        df_rank_latest_pivot = df_rank_latest.pivot(
            columns="param_name",
            index="tidm",
            values="value",
        )

        df_rank_latest_pivot = df_rank_latest_pivot.replace(
            ["nan", "None"], "NaN"
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
            df_rank_latest_pivot,
            left_index=True,
            right_index=True
            )

        # TODO Temp add Dividend Cover
        df_merged["Dividend Cover"] = str(np.nan)

        # Format column names
        df_merged = df_merged.rename(columns={
            "tidm": "tidm",
            "company_name": "company_name",
            "company_summary": "company_summary",
            "market__share_listing": "share_listing",
            "comp_type__company_type": "company_type",
            "industry__industry_name": "industry_name",
            "Share Price": "share_price",
            "Debt to Equity (D/E)": "debt_to_equity",
            "Current Ratio": "current_ratio",
            "Return on Equity (ROE)": "return_on_equity",
            "Equity (Book Value) Per Share": "equity_per_share",
            "Price to Earnings (P/E)": "price_to_earnings",
            "Price to Book Value (Equity)": "price_to_equity",
            "Annual Yield (Return)": "annual_return",
            "Free cash flow (FCF)": "fcf_growth_rate",
            "Dividend Payment": "dividend_payment",
            "Dividend Cover": "dividend_cover",
            "Revenue Growth": "revenue_growth",
            "EPS Growth": "eps_growth",
            "Dividend Growth": "dividend_growth",
            "Growth Quality": "growth_quality",
            "Revenue Growth (10 year)": "revenue_rowth_10",
            "Earnings Growth (10 year)": "earnings_growth_10",
            "Dividend Growth (10 year)": "dividend_growth_10",
            "Overall Growth (10 year)": "overall_growth_10",
            "Growth Rate (10 year)": "growth_rate_10",
            "Capital Employed": "capital_employed",
            "ROCE": "roce",
            "Median ROCE (10 year)": "median_roce_10",
            "Debt Ratio": "debt_ratio",
            "PE10": "pe_10",
            "DP10": "dp_10",
            "Growth Rate (10 year) Rank Value": "growth_rate_10_rank_value",
            "Growth Quality Rank Value": "growth_quality_rank_value",
            "Median ROCE (10 year) Rank Value": "median_roce_10_rank_value",
            "PE10 Rank Value": "pe_10_rank_value",
            "DP10 Rank Value": "dp_10_rank_value",
            "Growth Rate (10 year) Rank": "growth_rate_10_rank",
            "Growth Quality Rank": "growth_quality_rank",
            "Median ROCE (10 year) Rank": "median_roce_10_rank",
            "PE10 Rank": "pe_10_rank",
            "DP10 Rank": "dp_10_rank",
            "Defensive Rank": "defensive_rank",
            "DCF Intrinsic Value": "dcf_intrinsic_value",
            "Estimated Growth Rate": "estimated_growth_rate",
            "Estimated Discount Rate": "estimated_discount_rate",
            "Estimated Long Term Growth Rate": "estimated_long_term_growth_rate",
            })

        df_merged = df_merged.drop('id', axis=1)

        # Save to database
        # reports = [
        #     DashboardCompany(
        #         company=Companies.objects.get(id=row["company_id"]),
        #         parameter=Parameters.objects.get(id=row["parameter_id"]),
        #         time_stamp=row["time_stamp"],
        #         value=row["value"],
        #     )
        #     for i, row in df_unpivot.iterrows()
        # ]
        # CalculatedStats.objects.bulk_create(reports)

        # Save to csv
        # df_merged.to_csv("./file.csv", sep=',', index=False)
        print(df_merged)
