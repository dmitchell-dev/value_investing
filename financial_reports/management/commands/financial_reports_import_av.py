from django.core.management.base import BaseCommand
from ancillary_info.models import Companies, Params, ParamsApi
from financial_reports.models import FinancialReports
from api_import.vendors.alpha_vantage.client import AlphaVantageClient
from django.db import transaction

import pandas as pd
import numpy as np

from time import sleep


class Command(BaseCommand):
    help = "Imports Financial Data From Alpha Vantage API"

    def add_arguments(self, parser):
        parser.add_argument("--symbol", nargs="+", type=str)

    def handle(self, *args, **options):
        df_params_api = pd.DataFrame(list(ParamsApi.objects.get_params_api_joined()))
        df_companies = pd.DataFrame(list(Companies.objects.get_companies_joined()))

        # Specific symbols or all
        if options["symbol"] is None:
            comp_list = df_companies["tidm"].to_list()
        else:
            comp_list = options["symbol"]

        num_comps = len(comp_list)
        comp_num = 0
        api_call_num = 0
        total_rows_created = 0
        total_rows_updated = 0

        # For each report import data
        for company_tidm in comp_list:
            comp_num = comp_num + 1
            print(f"API Import {comp_num} of {num_comps}: {company_tidm}")

            # Get info oncurrent company
            comp_idx = df_companies[df_companies['tidm'] == company_tidm].index[0]
            curr_comp_id = df_companies["id"].iat[comp_idx]
            curr_comp_loc = df_companies["country__value"].iat[comp_idx]

            # For each statement type
            statement_list = ["INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW"]

            if curr_comp_loc == "US":

                for statement in statement_list:
                    api_call_num = api_call_num + 1

                    # Alpha Vantage limits requests to 5 every minute
                    if api_call_num % 5 == 0:
                        print("60 second delay")
                        sleep(65)

                    # AV API Share Import
                    av_import = AlphaVantageClient()
                    header, json_data = av_import.get_financial_data(
                        symbol=company_tidm, type=statement
                    )

                    # Convert to dataframe and unpivot
                    df_data = pd.DataFrame(json_data[header])
                    df_data = df_data.melt("fiscalDateEnding")

                    # Format dataframe to database schema
                    df_data = self._format_dataframe(df_data, curr_comp_id)

                    # Generate parameter_id and replace index
                    df_data = self._generate_param_id(df_params_api, df_data)

                    # Check datetime format
                    df_data = self._datetime_format(df_data)

                    # Update values
                    df_data = df_data.replace(to_replace='None', value=None)
                    df_data['value'] = df_data['value'].astype('float')
                    df_data['value'] = df_data['value']/1000000

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

    def _format_dataframe(self, df, company_id):
        df.insert(0, "company_id", [company_id] * df.shape[0])
        df.reset_index(drop=True, inplace=True)
        df.rename(
            columns={
                "fiscalDateEnding": "time_stamp",
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

    @staticmethod
    def _generate_param_id(df_params_api, df_data):

        param_id_list = []

        param_name_list = df_params_api["param_name_api"].tolist()
        param_id_list = df_params_api["param__id"].tolist()

        # Replace index with id
        df_data = df_data.reset_index()
        df_data["index_id"] = df_data["variable"].replace(
            param_name_list, param_id_list
        )

        # Filter out rows not in params list
        df_data = df_data[df_data["variable"].isin(param_name_list)]
        df_data = df_data.rename(columns={"index_id": "parameter_id"})
        df_data.drop(["variable"], axis=1, inplace=True)

        return df_data

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
