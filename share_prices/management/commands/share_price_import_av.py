from multiprocessing.sharedctypes import Value
from django.core.management.base import BaseCommand
from ancillary_info.models import Companies, Params
from share_prices.models import SharePrices
from api_import.vendors.alpha_vantage.client import AlphaVantageClient
import pandas as pd
import numpy as np
from time import sleep


class Command(BaseCommand):
    help = "Imports Share Prices From Alpha Vantage API"

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

            # Alpha Vantage limits requests to 5 every minute
            if comp_num % 5 == 0:
                print("60 second delay")
                sleep(65)

            print(f"API Import {comp_num} of {num_comps}: {company_tidm}")

            # Get info oncurrent company
            comp_idx = df_companies[df_companies['tidm'] == company_tidm].index[0]
            curr_comp_id = df_companies["id"].iat[comp_idx]
            curr_comp_loc = df_companies["country__value"].iat[comp_idx]

            # AV API Share Import
            try:
                av_import = AlphaVantageClient()
                header, json_data = av_import.get_share_data(
                    location=curr_comp_loc,
                    symbol=company_tidm,
                    type="TIME_SERIES_WEEKLY_ADJUSTED",
                )
            except IndexError:
                header = None
                json_data = None

            # Convert to dataframe
            df_data = pd.DataFrame.from_dict(json_data[header], orient="index")

            # Format dataframe to database schema
            df_data = self._format_dataframe(df_data, curr_comp_id)

            # Check datetime format
            df_data = self._datetime_format(df_data)

            # Update/Create split
            df_new, df_existing = self._create_update_split(df_data, company_tidm)

            # Update existing rows
            num_rows_updated = self._update_rows(df_existing, company_tidm)
            total_rows_updated = total_rows_updated + num_rows_updated

            # Create any new rows
            num_rows_created = self._create_rows(df_new)
            total_rows_created = total_rows_created + num_rows_created

        return f"Created: {str(total_rows_created)}, Updated: {str(total_rows_updated)}"

    def _format_dataframe(self, df, company_id):
        df.insert(0, "company_id", [company_id] * df.shape[0])
        df = df.drop(["1. open", "2. high", "3. low", "7. dividend amount"], axis=1)
        df["time_stamp"] = df.index
        df.reset_index(drop=True, inplace=True)
        df.rename(
            columns={
                "4. close": "value",
                "5. adjusted close": "value_adjusted",
                "6. volume": "volume",
            },
            inplace=True,
        )

        return df

    def _datetime_format(self, df):
        date_fmts = ("%Y-%m-%d", "%d/%m/%y", "%d/%m/%Y")
        for fmt in date_fmts:
            try:
                df["time_stamp"] = pd.to_datetime(df["time_stamp"], format=fmt)
                break
            except ValueError:
                pass

        # Order datetimes
        df.sort_values(by="time_stamp", inplace=True)

        return df

    def _create_update_split(self, new_df, company_tidm):

        existing_df = pd.DataFrame(
            list(SharePrices.objects.get_share_filtered(company_tidm))
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
            df_existing = None

        return df_new, df_existing

    def _create_rows(self, df_create):

        # Save to database
        reports = [
            SharePrices(
                company=Companies.objects.get(id=row["company_id"]),
                time_stamp=row["time_stamp"],
                value=row["value"],
                value_adjusted=row["value_adjusted"],
                volume=row["volume"],
            )
            for i, row in df_create.iterrows()
        ]
        list_of_objects = SharePrices.objects.bulk_create(reports)

        total_rows_added = len(list_of_objects)

        return total_rows_added

    def _update_rows(self, df_update, company_tidm):

        param_list = ["value", "value_adjusted", "volume"]

        extsting_qs = SharePrices.objects.filter(
            company__tidm=company_tidm
            )

        # For each item in the queryset, update with associated value in df
        for item in extsting_qs.iterator():
            filter_ts_idx = str(item.time_stamp)

            updated_value = df_update.query(
                f'time_stamp_txt == "{filter_ts_idx}"'
                )['value'].values[0]
            item.value = float(updated_value)

            updated_value_adjusted = df_update.query(
                f'time_stamp_txt == "{filter_ts_idx}"'
                )['value_adjusted'].values[0]
            item.value_adjusted = float(updated_value_adjusted)

            updated_volume = df_update.query(
                f'time_stamp_txt == "{filter_ts_idx}"'
                )['volume'].values[0]
            item.volume = float(updated_volume)

        for param in param_list:
            num_rows_updated = SharePrices.objects.bulk_update(
                extsting_qs,
                [param]
                )

        return num_rows_updated
