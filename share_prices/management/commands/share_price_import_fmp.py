from django.core.management.base import BaseCommand
from ancillary_info.models import Companies
from share_prices.models import SharePrices
from api_import.vendors.fmp.client import FMPClient
from django.db import transaction

import pandas as pd
import numpy as np


class Command(BaseCommand):
    help = "Imports Share Prices From FMP API (US companies only)"

    def add_arguments(self, parser):
        parser.add_argument("--symbol", nargs="+", type=str)
        parser.add_argument("--from_date", type=str, help="Start date YYYY-MM-DD")
        parser.add_argument("--to_date", type=str, help="End date YYYY-MM-DD")

    def handle(self, *args, **options):
        df_companies = pd.DataFrame(list(Companies.objects.get_companies_joined()))

        if options["symbol"] is None:
            comp_list = df_companies[df_companies["country__value"] == "US"]["tidm"].to_list()
        else:
            comp_list = options["symbol"]

        num_comps = len(comp_list)
        comp_num = 0
        total_rows_created = 0
        total_rows_updated = 0

        fmp = FMPClient()

        for company_tidm in comp_list:
            comp_num += 1
            print(f"FMP Share Price Import {comp_num} of {num_comps}: {company_tidm}")

            comp_idx = df_companies[df_companies["tidm"] == company_tidm].index[0]
            curr_comp_id = df_companies["id"].iat[comp_idx]
            curr_comp_loc = df_companies["country__value"].iat[comp_idx]

            if curr_comp_loc != "United States":
                print(f"  Skipping {company_tidm} — FMP free tier is US only")
                continue

            response = fmp.get_share_price_history(
                symbol=company_tidm,
                from_date=options.get("from_date"),
                to_date=options.get("to_date"),
            )

            # FMP historical-price-full returns a dict with 'historical' key
            if not response or not isinstance(response, dict):
                print(f"  No data returned for {company_tidm}")
                continue

            historical = response.get("historical", [])
            if not historical:
                print(f"  No historical data for {company_tidm}")
                continue

            df_data = pd.DataFrame(historical)

            df_data = self._format_dataframe(df_data, curr_comp_id)
            df_data = self._datetime_format(df_data)

            df_new, df_new_existing, df_old_existing = self._create_update_split(
                df_data, company_tidm
            )

            if not df_new_existing.empty:
                num_rows_updated = self._update_rows(df_new_existing, df_old_existing)
                total_rows_updated += num_rows_updated

            if not df_new.empty:
                num_rows_created = self._create_rows(df_new)
                total_rows_created += num_rows_created

        return f"Created: {str(total_rows_created)}, Updated: {str(total_rows_updated)}"

    @staticmethod
    def _format_dataframe(df, company_id):
        df.insert(0, "company_id", company_id)
        df.rename(
            columns={
                "date": "time_stamp",
                "close": "value",
                "adjClose": "value_adjusted",
                "volume": "volume",
            },
            inplace=True,
        )
        keep_cols = ["company_id", "time_stamp", "value", "value_adjusted", "volume"]
        df = df[[c for c in keep_cols if c in df.columns]]
        df.reset_index(drop=True, inplace=True)
        return df

    @staticmethod
    def _datetime_format(df):
        date_fmts = ("%Y-%m-%d", "%d/%m/%y", "%d/%m/%Y")
        for fmt in date_fmts:
            try:
                df["time_stamp"] = pd.to_datetime(df["time_stamp"], format=fmt)
                break
            except ValueError:
                pass
        df.sort_values(by="time_stamp", inplace=True)
        return df

    def _create_update_split(self, new_df, company_tidm):
        existing_old_df = pd.DataFrame(
            list(SharePrices.objects.get_share_filtered(company_tidm))
        )

        if not new_df.empty:
            new_df["time_stamp_txt"] = new_df["time_stamp"].astype(str)

        if not existing_old_df.empty:
            existing_old_df["time_stamp_txt"] = existing_old_df["time_stamp"].astype(str)

            split_idx = np.where(
                new_df["time_stamp_txt"].isin(existing_old_df["time_stamp_txt"]),
                "existing",
                "new",
            )

            df_new_existing = new_df[split_idx == "existing"]
            df_old_existing = existing_old_df
            df_new = new_df[split_idx == "new"]
        else:
            df_new = new_df
            df_new_existing = pd.DataFrame()
            df_old_existing = pd.DataFrame()

        return df_new, df_new_existing, df_old_existing

    def _create_rows(self, df_create):
        reports = [
            SharePrices(
                company=Companies.objects.get(id=row["company_id"]),
                time_stamp=row["time_stamp"],
                value=row["value"],
                value_adjusted=row.get("value_adjusted"),
                volume=row.get("volume"),
            )
            for i, row in df_create.iterrows()
        ]
        list_of_objects = SharePrices.objects.bulk_create(reports)
        return len(list_of_objects)

    def _update_rows(self, df_new_existing, df_old_existing):
        """Update rows where values have changed."""
        num_rows_updated = 0

        for col in ["value", "value_adjusted"]:
            df_new_existing[col] = df_new_existing[col].astype("float").map("{:.2f}".format)
            df_old_existing[col] = df_old_existing[col].astype("float").map("{:.2f}".format)
        df_new_existing["volume"] = df_new_existing["volume"].astype("float").map("{:.0f}".format)
        df_old_existing["volume"] = df_old_existing["volume"].astype("float").map("{:.0f}".format)

        new_midx = pd.MultiIndex.from_arrays(
            [df_new_existing[col] for col in ["time_stamp_txt", "value", "value_adjusted", "volume"]]
        )
        df_new_existing["mul_col_idx"] = new_midx

        existing_midx = pd.MultiIndex.from_arrays(
            [df_old_existing[col] for col in ["time_stamp_txt", "value", "value_adjusted", "volume"]]
        )
        df_old_existing["mul_col_idx"] = existing_midx

        split_idx = np.where(new_midx.isin(existing_midx), "existing", "new")
        df_to_update = df_new_existing[split_idx == "new"]

        if not df_to_update.empty:
            df_to_update = df_to_update.reset_index()
            df_to_update["id"] = np.nan

            for index, row in df_to_update.iterrows():
                df_to_update.at[index, "id"] = df_old_existing[
                    df_old_existing["time_stamp_txt"].isin([row["time_stamp_txt"]])
                ]["id"].values[0]
            df_to_update = df_to_update.set_index("id")

            with transaction.atomic():
                for index, row in df_to_update.iterrows():
                    SharePrices.objects.filter(id=index).update(
                        value=row["value"],
                        value_adjusted=row["value_adjusted"],
                        volume=row["volume"],
                    )
                    num_rows_updated += 1

        return num_rows_updated
