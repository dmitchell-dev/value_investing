import pandas as pd

from ..ancillary_info.ancillary_info import AncillaryInfo
from .ranking_stats_objects import RankingStatsObjects
from ..common.mysql_base import session_factory, engine

from ..calculated_stats.calculated_stats import CalculatedStats

from .manager import create_growth_list

from datetime import datetime


class RankingStats:
    def __init__(self):
        session_factory()

    def populate_tables(self):
        # Get ancillary data
        df_companies = AncillaryInfo().get_companies_joined()
        df_params = AncillaryInfo().get_parameters_joined()

        # Calculate rank for each type
        ranktype_list = [
            "Growth Rate (10 year)",
            "Growth Quality",
            "Median ROCE (10 year)",
            "PE10",
            "DP10",
        ]

        rank_df_list = []
        values_df_list = []
        num_ranks = len(ranktype_list)
        rank_num = 0

        for rank_type in ranktype_list:

            print(f"Rank {rank_num + 1} of {num_ranks}, {rank_type}")

            calculated_stats_instance = CalculatedStats()
            df = calculated_stats_instance.get_table_joined_filtered(rank_type)

            # Offset dates by 1 day to account for companies
            # reporting on first of the year
            df["time_stamp_delta"] = df["time_stamp"] + pd.DateOffset(days=-1)
            df["year"] = pd.DatetimeIndex(df["time_stamp_delta"]).year

            # Remove Duplicates and take last value
            # This accounts for companies reporting
            # twice in a year and take last report
            df2 = df.drop_duplicates(subset=["tidm", "year"], keep="last")

            # Pivot dataframe
            df_pivot = (
                df2.pivot(columns="year", index="tidm", values="value")
                .replace(to_replace="None", value=None)
                .astype("float")
            )
            # df_pivot

            df_growth_values, df_growth_rank = create_growth_list(
                df_pivot, ranktype_list, rank_num
                )
            values_df_list.append(df_growth_values)
            rank_df_list.append(df_growth_rank)

            rank_num = rank_num + 1

        df_growth_values = pd.concat(values_df_list, axis=1)

        # Growth Rank
        df_growth_rank = pd.concat(rank_df_list, axis=1)
        df_growth_rank["Defensive Rank"] = df_growth_rank.sum(axis=1)
        df_growth_rank = df_growth_rank.sort_values(
            by="Defensive Rank",
            ascending=True
            )

        # Combine back together
        df_rank_both = pd.concat([df_growth_values, df_growth_rank], axis=1)

        # Replace with ids
        df_unpivot = self._replace_with_id(
            df_rank_both, df_params, df_companies
            )

        # Populate database
        df_unpivot.to_sql(
            RankingStatsObjects.__tablename__,
            con=engine,
            if_exists="append",
            index=False,
        )

    def _replace_with_id(self, df_rank_both, df_params, df_companies):
        # Generate parameter_id and replace index
        param_id_list = []
        param_list = df_rank_both.columns
        for param in param_list:

            param_id = df_params[df_params.param_name == param].id.values[0]
            param_id_list.append(param_id)

        df_rank_both.columns = param_id_list

        # company id
        company_id_list = []
        company_list = df_rank_both.index
        for company in company_list:

            company_id = df_companies[df_companies.tidm == company].id.values[
                0
            ]
            company_id_list.append(company_id)

        df_rank_both.index = company_id_list

        df_unpivot = pd.melt(
            df_rank_both,
            var_name="parameter_id",
            value_name="value",
            ignore_index=False
        )

        time_stamp_now = datetime.now()

        df_unpivot['time_stamp'] = time_stamp_now
        df_unpivot["company_id"] = df_unpivot.index

        return df_unpivot
