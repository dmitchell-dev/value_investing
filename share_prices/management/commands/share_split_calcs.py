from django.core.management.base import BaseCommand
from ancillary_info.models import Companies
from share_prices.models import SharePrices, ShareSplits

import pandas as pd
import numpy as np


class Command(BaseCommand):
    help = "Calculates Stock Splits for each company"

    def add_arguments(self, parser):
        parser.add_argument("--symbol", nargs="+", type=str)

    def handle(self, *args, **options):
        df_companies = pd.DataFrame(list(Companies.objects.get_companies_joined()))

        # Specific symbols or all
        if options["symbol"] is None:
            comp_list = df_companies["tidm"].to_list()
        else:
            comp_list = options["symbol"]

        num_comps = len(comp_list)
        comp_num = 0
        total_rows_created = 0
        total_rows_updated = 0

        # For each report import data
        for company_tidm in comp_list:
            comp_num = comp_num + 1

            print(f"API Import {comp_num} of {num_comps}: {company_tidm}")

            # Get info oncurrent company
            comp_idx = df_companies[df_companies['tidm'] == company_tidm].index[0]
            curr_comp_id = df_companies["id"].iat[comp_idx]

            df_data = pd.DataFrame(
                list(SharePrices.objects.get_share_joined_filtered(company_tidm))
            )

            # Detect and calculate stock splits
            df_data["share_split"] = (
                df_data["value"].div(df_data["value_adjusted"]).diff().abs()
            )

            df_data_index = df_data["share_split"] > 0.1

            df_data_filtered = df_data[df_data_index]

            if not df_data_filtered.empty:

                df_data_filtered.insert(
                    0, "company_id", [curr_comp_id] * df_data_filtered.shape[0]
                )

                # Update/Create split
                df_new, df_existing = self._create_update_split(df_data_filtered, company_tidm)

                # Update existing rows
                if not df_existing.empty:
                    num_rows_updated = self._update_rows(df_existing, company_tidm)
                    total_rows_updated = total_rows_updated + num_rows_updated

                # Create any new rows
                if not df_new.empty:
                    num_rows_created = self._create_rows(df_new)
                    total_rows_created = total_rows_created + num_rows_created

        return f"Created: {str(total_rows_created)}, Updated: {str(total_rows_updated)}"

    def _create_update_split(self, new_df, company_tidm):

        existing_df = pd.DataFrame(
            list(ShareSplits.objects.get_share_filtered(company_tidm))
            )

        if not existing_df.empty:
            new_df['time_stamp_txt'] = new_df['time_stamp'].astype(str)
            existing_df['time_stamp_txt'] = existing_df['time_stamp'].astype(str)
            split_idx = np.where(
                new_df["time_stamp_txt"].isin(existing_df["time_stamp_txt"]), "existing", "new"
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
            ShareSplits(
                company=Companies.objects.get(id=row["company_id"]),
                time_stamp=row["time_stamp"],
                value=row["value"],
            )
            for i, row in df_create.iterrows()
        ]
        list_of_objects = ShareSplits.objects.bulk_create(reports)

        total_rows_added = len(list_of_objects)

        return total_rows_added

    def _update_rows(self, df_update, company_tidm):

        param_list = ["value"]

        extsting_qs = ShareSplits.objects.filter(
            company__tidm=company_tidm
            )

        # For each item in the queryset, update with associated value in df
        for item in extsting_qs.iterator():
            filter_ts_idx = str(item.time_stamp)

            updated_value = df_update.query(
                f'time_stamp_txt == "{filter_ts_idx}"'
                )['value'].values[0]
            item.value = float(updated_value)

        for param in param_list:
            num_rows_updated = ShareSplits.objects.bulk_update(
                extsting_qs,
                [param]
                )

        return num_rows_updated
