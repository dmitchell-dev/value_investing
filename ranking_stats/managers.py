from django.db.models import QuerySet
import math
import pandas as pd


class RankingStatsQueryset(QuerySet):
    def get_table_joined_filtered(self, rank_type):
        return self.values(
            "time_stamp",
            "value",
            "company__tidm",
            "parameter__param_name",
        ).filter(parameter__param_name=rank_type)

    def get_table_joined(self):
        return self.values(
            "time_stamp",
            "value",
            "company__tidm",
            "parameter__param_name",
        )


def create_growth_list(df_pivot, ranktype_list, rank_num):
    # Create Growth list
    last_list = []
    tidm_list = df_pivot.index

    # Get last value if exists,
    # if not, then take second to last
    for i, row in df_pivot.iterrows():
        current_value = row.values[df_pivot.shape[1] - 1]

        if math.isnan(current_value):
            current_value = row.values[df_pivot.shape[1] - 2]

        last_list.append(current_value)

    # Convert to dataframe
    df_growth_values = pd.DataFrame(data=last_list)
    df_growth_values.columns = [f"{ranktype_list[rank_num]} Rank Value"]
    df_growth_values.index = tidm_list

    # Replace NaN with -999
    df_growth_values = df_growth_values.fillna(-999)
    if ranktype_list[rank_num] == "PE10" or ranktype_list[rank_num] == "DP10":
        mask = df_growth_values[f"{ranktype_list[rank_num]} Rank Value"].gt(0)
        df_growth_values = pd.concat(
            [
                df_growth_values[mask].sort_values(
                    f"{ranktype_list[rank_num]} Rank Value"
                ),
                df_growth_values[~mask].sort_values(
                    f"{ranktype_list[rank_num]} Rank Value", ascending=False
                ),
            ]
        )
    else:
        df_growth_values = df_growth_values.sort_values(
            by=f"{ranktype_list[rank_num]} Rank Value", ascending=False
        )

    # Rank Dataframe
    df_growth_rank = pd.DataFrame()
    df_growth_rank[f"{ranktype_list[rank_num]} Rank"] = range(len(df_growth_values))
    df_growth_rank.index = df_growth_values.index

    return (df_growth_values, df_growth_rank)
