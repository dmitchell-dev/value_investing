from django.core.management.base import BaseCommand
from ancillary_info.models import Companies, Params, ParamsApi
from financial_reports.models import FinancialReports
from api_import.vendors.alpha_vantage.client import AlphaVantageClient

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

                    # Update/Create split
                    df_new, df_existing = self._create_update_split(df_data, company_tidm)

                    # Update existing rows
                    if not df_existing.empty:
                        num_rows_updated = self._update_rows(df_existing, company_tidm)
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

        existing_df = pd.DataFrame(
            list(FinancialReports.objects.get_financial_data_filtered(company_tidm))
            )

        if not new_df.empty:
            new_df['time_stamp_txt'] = new_df['time_stamp'].astype(str)

        if not existing_df.empty:
            existing_df['time_stamp_txt'] = existing_df['time_stamp'].astype(str)

            new_midx = pd.MultiIndex.from_arrays(
                [new_df[col] for col in ['time_stamp_txt', 'parameter_id']]
                )
            existing_midx = pd.MultiIndex.from_arrays(
                [existing_df[col] for col in ['time_stamp_txt', 'parameter']]
                )

            split_idx = np.where(
                new_midx.isin(existing_midx), "existing", "new"
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

    def _update_rows(self, df_update, company_tidm):

        df_update["mul_idx_col"] = df_update["parameter_id"].astype(str) + "_" + df_update["time_stamp_txt"]

        extsting_qs = FinancialReports.objects.filter(
            company__tidm=company_tidm
            )

        # For each item in the queryset, update with associated value in df
        for item in extsting_qs.iterator():
            filter_mul_idx = str(item.parameter_id)+"_"+str(item.time_stamp)

            # Check if date exists in df_update
            # AV does not go back as far as TIKR
            if not df_update[df_update['mul_idx_col'].isin([filter_mul_idx])].empty:

                updated_value = df_update.query(
                    f'mul_idx_col == "{filter_mul_idx}"'
                    )['value'].values[0]

                item.value = updated_value

        num_rows_updated = FinancialReports.objects.bulk_update(
            extsting_qs,
            ["value"]
            )

        return num_rows_updated
