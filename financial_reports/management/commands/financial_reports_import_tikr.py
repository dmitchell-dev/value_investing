from turtle import update
from django.core.management.base import BaseCommand
from financial_reports.models import FinancialReports
from ancillary_info.models import Params, Companies, ParamsApi
from django.db import transaction

import pandas as pd
import numpy as np

import os


class Command(BaseCommand):
    help = "Populates Static tables from csv files"

    def add_arguments(self, parser):
        parser.add_argument("--symbol", nargs="+", type=str)

    def handle(self, *args, **options):
        df_params_api = pd.DataFrame(list(ParamsApi.objects.get_params_api_joined()))
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

            # Generate parameter_id and replace index
            df_data = self._generate_param_id(df_params_api, df_data)

            # company id
            company_id = df_companies[
                df_companies["tidm"] == company_tidm
            ].id.values[0]

            # Create list of columns
            df_items = df_data.items()
            output_list = []
            for label, content in df_items:
                output_list.append([content])

            # Format dataframe ready to import into database
            df_unpivot = pd.melt(
                df_data, var_name="time_stamp", value_name="value", ignore_index=False
            )
            df_unpivot["company_id"] = company_id
            df_unpivot["parameter_id"] = df_unpivot.index

            # Format value column
            df_unpivot["value"] = (
                df_unpivot["value"]
                .replace(",", "", regex=True)
                .str.strip(")")
                .str.replace("\(", "-")
            )

            # Replace infinity values
            df_unpivot["value"] = df_unpivot["value"].replace(
                ["Infinity", "-Infinity"], None
            )

            # Check datetime format
            df_unpivot = self._datetime_format(df_unpivot)

            df_unpivot = df_unpivot.replace(to_replace='None', value=None)

            # Update/Create split
            df_new, df_new_existing, df_old_existing = self._create_update_split(df_unpivot, company_tidm)

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
        df_income = pd.read_excel(
            f"data/company_reports/{current_company_filename}",
            sheet_name="income_statement",
            index_col="Income Statement",
            skiprows=1,
        )

        df_balance = pd.read_excel(
            f"data/company_reports/{current_company_filename}",
            sheet_name="balance_sheet",
            index_col="Balance Sheet",
            skiprows=1,
        )

        df_cash = pd.read_excel(
            f"data/company_reports/{current_company_filename}",
            sheet_name="cash_flow_statement",
            index_col="Cash Flow Statement",
            skiprows=1,
        )

        # TIKR sometimes has duplicate Operating Expenses in Income Statement
        income_index = np.where(df_income.index == "Other Operating Expenses")[0]
        if income_index.size == 2:
            df_income.drop(df_income.index[income_index[0]], inplace=True)
        # TIKR has duplicate Net Income in Cash Flow Statement
        df_cash.drop(df_cash[df_cash.index == "Net Income"].index, inplace=True)

        # Stack dataframes
        df = pd.concat([df_income, df_balance, df_cash], axis=0)

        # Drop empty rows with empty index
        df.drop(df[df.index.isnull()].index, inplace=True)

        # Drop last LTM Column if exists
        if "LTM" in df.columns:
            df.drop(["LTM"], axis=1, inplace=True)

        # Drop leading spaces in index names
        df.index = df.index.str.strip()

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
    def _generate_param_id(df_params_api, df_data):

        param_id_list = []

        param_name_list = df_params_api["param_name_api"].tolist()
        param_id_list = df_params_api["param__id"].tolist()

        # Replace index with id
        df_data = df_data.reset_index()
        df_data["index_id"] = df_data["index"].replace(param_name_list, param_id_list)

        # Filter out rows not in params list
        df_data = df_data[df_data["index"].isin(param_name_list)]

        # Replace index
        df_data.drop(["index"], axis=1, inplace=True)
        df_data.set_index("index_id", inplace=True)

        return df_data

    @staticmethod
    def _datetime_format(df):
        date_fmts = ("%m/%d/%y", "%d/%m/%y", "%d/%m/%Y")

        # Add leading zeros to dates
        split_dates = df["time_stamp"].str.split("/", expand=True)
        df["time_stamp"] = split_dates.iloc[:, 0:3].apply(
            lambda x: "/".join(x.astype(str)), axis=1
        )

        # Convert to datetime
        for fmt in date_fmts:
            try:
                df["time_stamp"] = pd.to_datetime(df["time_stamp"], format=fmt)
                break
            except ValueError:
                pass

        return df

    def _create_update_split(self, new_df, company_tidm):

        existing_old_df = pd.DataFrame(
            list(FinancialReports.objects.get_financial_data_filtered(company_tidm))
            )

        if not new_df.empty:
            new_df['time_stamp_txt'] = new_df['time_stamp'].astype(str)

        if not existing_old_df.empty:
            existing_old_df['time_stamp_txt'] = existing_old_df['time_stamp'].astype(str)

            new_midx = pd.MultiIndex.from_arrays(
                [new_df[col] for col in ['time_stamp_txt', 'parameter_id']]
                )
            existing_midx = pd.MultiIndex.from_arrays(
                [existing_old_df[col] for col in ['time_stamp_txt', 'parameter']]
                )

            split_idx = np.where(
                new_midx.isin(existing_midx), "existing", "new"
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
            FinancialReports(
                company=Companies.objects.get(id=row["company_id"]),
                parameter=Params.objects.get(id=row["parameter_id"]),
                time_stamp=row["time_stamp"],
                value=row["value"],
            )
            for i, row in df_create.iterrows()
        ]
        list_of_objects = FinancialReports.objects.bulk_create(reports)

        total_rows_added = len(list_of_objects)

        return total_rows_added

    def _update_rows(self, df_new_existing, df_old_existing):
        """Checks if the values in the new df are different from the old df,
        if yes, updates the database"""

        num_rows_updated = 0

        # Format value columns correctly
        df_new_existing['value'] = df_new_existing['value'].astype('float')
        df_old_existing['value'] = df_old_existing['value'].astype('float')
        df_new_existing['value'] = df_new_existing['value'].map('{:.2f}'.format)
        df_old_existing['value'] = df_old_existing['value'].map('{:.2f}'.format)

        # Create multi columnindexes for both with and without value
        new_midx_value = pd.MultiIndex.from_arrays(
            [df_new_existing[col] for col in ['time_stamp_txt', 'parameter_id', 'value']]
            )
        new_midx = pd.MultiIndex.from_arrays(
            [df_new_existing[col] for col in ['time_stamp_txt', 'parameter_id']]
            )
        df_new_existing['mul_col_idx'] = new_midx

        existing_midx_value = pd.MultiIndex.from_arrays(
            [df_old_existing[col] for col in ['time_stamp_txt', 'parameter', 'value']]
            )
        existing_midx = pd.MultiIndex.from_arrays(
            [df_old_existing[col] for col in ['time_stamp_txt', 'parameter']]
            )
        df_old_existing['mul_col_idx'] = existing_midx

        split_idx = np.where(
            new_midx_value.isin(existing_midx_value), "existing", "new"
        )

        # Only values to update
        df_to_update = df_new_existing[split_idx == "new"]

        if not df_to_update.empty:
            df_to_update['id'] = np.nan

            df_to_update = df_to_update.reset_index()

            # Transfer row id across to new df
            for index, row in df_to_update.iterrows():
                df_to_update.at[index, 'id'] = df_old_existing[df_old_existing['mul_col_idx'].isin([row['mul_col_idx']])]['id'].values[0]
            df_to_update = df_to_update.set_index('id')

            # Update Database
            with transaction.atomic():
                for index, row in df_to_update.iterrows():
                    # print(index, row['value'])
                    FinancialReports.objects.filter(id=index).update(value=row['value'])
                num_rows_updated = num_rows_updated + 1

        return num_rows_updated
