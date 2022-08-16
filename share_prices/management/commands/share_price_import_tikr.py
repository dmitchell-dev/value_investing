from django.core.management.base import BaseCommand
from share_prices.models import SharePrices
from ancillary_info.models import Companies
from django.db import transaction

import pandas as pd
import numpy as np

import os


class Command(BaseCommand):
    help = "Populates Static tables from csv files"

    def add_arguments(self, parser):
        parser.add_argument("--symbol", nargs="+", type=str)

    def handle(self, *args, **options):
        df_companies = pd.DataFrame(list(Companies.objects.get_companies_joined()))

        # Specific symbols or all
        if options["symbol"] is None:
            file_list = self._get_report_list()
        else:
            file_list = ["single_company"]
            file_list_single = self._get_report_list()

        num_files = len(file_list)
        file_num = 0
        total_rows_created = 0
        total_rows_updated = 0

        # For each report import data
        for current_company_filename in file_list:
            file_num = file_num + 1
            print(f"file {file_num} of {num_files}, {current_company_filename}")

            # Process filename
            if options["symbol"] is None:
                company_tidm = self._process_filename(current_company_filename)
            else:
                company_tidm = options["symbol"][0]
                current_company_filename = self._get_filename(file_list_single, company_tidm)

            # Get company report data
            df_data = self._import_reporting_data(current_company_filename)

            # company id
            company_id = df_companies[
                df_companies["tidm"] == company_tidm
            ].id.values[0]

            # Check datetime format
            df_data.insert(0, "company_id", [company_id] * df_data.shape[0])
            # df_data = self._datetime_format(df_data, company_id)

            # Format Column Names
            df_data = self._format_col_names(df_data, company_tidm)

            df_data = df_data.replace(to_replace='None', value=None)

            # Update/Create split
            df_new, df_new_existing, df_old_existing = self._create_update_split(df_data, company_tidm)

            # Update existing rows
            if not df_new_existing.empty:
                num_rows_updated = self._update_rows(df_new_existing, df_old_existing)
                total_rows_updated = total_rows_updated + num_rows_updated

            # Create any new rows
            if not df_new.empty:
                num_rows_created = self._create_rows(df_new)
                total_rows_created = total_rows_created + num_rows_created

        return f"Created: {str(total_rows_created)}, Updated: {str(total_rows_updated)}"

    @staticmethod
    def _import_reporting_data(current_company_filename):
        df = pd.read_excel(
            f"data/company_reports/{current_company_filename}",
            sheet_name="share_price",
        )

        # Drop empty rows with empty index
        df.drop(df[df.index.isnull()].index, inplace=True)

        # TODO does this do anything??
        df = df.where((pd.notnull(df)), None)

        return df

    @staticmethod
    def _get_report_list():
        # Import each file, process and save to database
        # Get list of reports
        path = "data/company_reports"
        file_list = []
        for files in os.listdir(path):
            file_list.append(files)

        return file_list

    @staticmethod
    def _process_filename(current_company_filename):

        # Get company tidm for associated id
        company_tidm = current_company_filename.split("_")[0]

        return company_tidm

    @staticmethod
    def _get_filename(file_list_single, company_tidm):

        # Get company tidm for associated id
        tidm_list = [tidm.split('_', 1)[0] for tidm in file_list_single]
        tidm_idx = tidm_list.index(company_tidm)
        current_company_filename = file_list_single[tidm_idx]

        return current_company_filename

    @staticmethod
    def _datetime_format(df, company_id):
        df.insert(0, "company_id", [company_id] * df.shape[0])
        date_fmts = ("%Y/%m/%d", "%m/%d/%y", "%d/%m/%y", "%d/%m/%Y")

        # Add leading zeros to dates
        split_dates = df["DateTime"].str.split("/", expand=True)
        df["DateTime"] = split_dates.iloc[:, 0:3].apply(
            lambda x: "/".join(x.astype(str)), axis=1
        )

        # Convert to datetime
        for fmt in date_fmts:
            try:
                df["DateTime"] = pd.to_datetime(df["DateTime"], format=fmt)
                break
            except ValueError:
                pass

        return df

    @staticmethod
    def _format_col_names(df, tidm):

        value_col = f"{tidm} Price Close"
        vol_col = f"{tidm} Volume"

        # Rename Columns
        df = df.rename(columns={'DateTime': 'time_stamp', value_col: 'value', vol_col: 'volume'})

        # Add adjusted column
        df['value_adjusted'] = df['value']

        # Delete Columns
        df = df.drop(['OHLC (open)', 'OHLC (high)', 'OHLC (low)', 'OHLC (close)'], axis=1)

        df = df.astype(object).where(pd.notnull(df), None)

        return df

    def _create_update_split(self, new_df, company_tidm):

        existing_old_df = pd.DataFrame(
            list(SharePrices.objects.get_share_filtered(company_tidm))
            )

        if not new_df.empty:
            new_df['time_stamp_txt'] = new_df['time_stamp'].astype(str)
            new_df['time_stamp_txt'] = new_df['time_stamp_txt'].str.replace(' 00:00:00','')

        if not existing_old_df.empty:
            existing_old_df['time_stamp_txt'] = existing_old_df['time_stamp'].astype(str)

            split_idx = np.where(
                new_df["time_stamp_txt"].isin(existing_old_df["time_stamp_txt"]), "existing", "new"
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

    def _update_rows(self, df_new_existing, df_old_existing):
        """Checks if the values in the new df are different from the old df,
        if yes, updates the database"""

        num_rows_updated = 0

        # Format value columns correctly
        df_new_existing['value'] = df_new_existing['value'].astype('float').map('{:.2f}'.format)
        df_new_existing['value_adjusted'] = df_new_existing['value_adjusted'].astype('float').map('{:.2f}'.format)
        df_new_existing['volume'] = df_new_existing['volume'].astype('float').map('{:.0f}'.format)

        df_old_existing['value'] = df_old_existing['value'].astype('float').map('{:.2f}'.format)
        df_old_existing['value_adjusted'] = df_old_existing['value_adjusted'].astype('float').map('{:.2f}'.format)
        df_old_existing['volume'] = df_old_existing['volume'].astype('float').map('{:.0f}'.format)

        new_midx = pd.MultiIndex.from_arrays(
            [df_new_existing[col] for col in ['time_stamp_txt', 'value', 'value_adjusted', 'volume']]
            )
        df_new_existing['mul_col_idx'] = new_midx

        existing_midx = pd.MultiIndex.from_arrays(
            [df_old_existing[col] for col in ['time_stamp_txt', 'value', 'value_adjusted', 'volume']]
            )
        df_old_existing['mul_col_idx'] = existing_midx

        split_idx = np.where(
            new_midx.isin(existing_midx), "existing", "new"
        )

        # Only values to update
        df_to_update = df_new_existing[split_idx == "new"]

        if not df_to_update.empty:
            df_to_update['id'] = np.nan

            df_to_update = df_to_update.reset_index()

            # Transfer row id across to new df
            for index, row in df_to_update.iterrows():
                df_to_update.at[index, 'id'] = df_old_existing[df_old_existing['time_stamp_txt'].isin([row['time_stamp_txt']])]['id'].values[0]
            df_to_update = df_to_update.set_index('id')

            # Update Database
            with transaction.atomic():
                for index, row in df_to_update.iterrows():
                    # print(index, row['value'])
                    SharePrices.objects.filter(id=index).update(value=row['value'])
                    num_rows_updated = num_rows_updated + 1

            with transaction.atomic():
                for index, row in df_to_update.iterrows():
                    # print(index, row['value'])
                    SharePrices.objects.filter(id=index).update(value_adjusted=row['value_adjusted'])
                    num_rows_updated = num_rows_updated + 1

            with transaction.atomic():
                for index, row in df_to_update.iterrows():
                    # print(index, row['value'])
                    SharePrices.objects.filter(id=index).update(volume=row['volume'])
                    num_rows_updated = num_rows_updated + 1

        return num_rows_updated
