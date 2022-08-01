# import csv
# from django.conf import settings
from django.core.management.base import BaseCommand
from ancillary_info.models import (
    Params,
    Companies,
    DcfVariables,
)

import pandas as pd


class Command(BaseCommand):
    help = "Populates Static tables from csv files"

    def add_arguments(self, parser):
        parser.add_argument("--symbol", nargs="+", type=str)

    def handle(self, *args, **options):
        # Default Values
        dcf_dict = {
            "Estimated Growth Rate": 0.06,
            "Estimated Discount Rate": 0.1,
            "Estimated Long Term Growth Rate": 0.03,
        }

        dcf_key_list = list(dcf_dict.keys())
        dcf_value_list = list(dcf_dict.values())

        # Get ancillary data
        df_params = pd.DataFrame(list(Params.objects.get_params_joined()))
        df_companies = pd.DataFrame(list(Companies.objects.get_companies_joined()))

        # Specific symbols or all
        if options["symbol"] is None:
            comp_list = df_companies["tidm"].to_list()
        else:
            comp_list = options["symbol"]

        # Populate values for each company
        # Get list of companies
        num_companies = len(comp_list)
        company_num = 0
        num_rows_created = 0
        num_rows_updated = 0

        for company_tidm in comp_list:
            company_num = company_num + 1
            print(f"Company {company_num} of {num_companies}, {company_tidm}")

            # company id
            company_id = df_companies[df_companies["tidm"] == company_tidm].id.values[0]

            data_dict = {
                "parameter_id": [dcf_key_list[0], dcf_key_list[1], dcf_key_list[2]],
                "company_id": [company_id, company_id, company_id],
                "value": [dcf_value_list[0], dcf_value_list[1], dcf_value_list[2]],
            }
            df_data = pd.DataFrame(data_dict)

            # Generate parameter_id and replace index
            df_data = self._generate_param_id(df_params, df_data)

            # Split ready for create or update
            (df_create, df_update) = self._create_update_split(
                df_data,
                company_tidm
                )

            # Create new companies
            if not df_create.empty:
                num_rows_created = self._create_rows(df_create)
                print(f"Dashboard Create Complete: {num_rows_created} rows updated")

            # Update existing companies
            if not df_update.empty:
                num_rows_updated = self._update_rows(df_update, company_tidm)
                print(f"Dashboard Update Complete: {num_rows_updated} rows updated")

            return f"Created: {str(num_rows_created)}, Updated: {str(num_rows_updated)}"

    @staticmethod
    def _generate_param_id(df_params, df_data):

        param_id_list = []

        param_name_list = df_params["param_name"].tolist()
        param_id_list = df_params["id"].tolist()

        # Replace index with id
        df_data = df_data.reset_index()
        df_data["parameter_id"] = df_data["parameter_id"].replace(
            param_name_list, param_id_list
        )

        return df_data

    def _create_update_split(self, new_df, company_tidm):
        existing_df = pd.DataFrame(list(DcfVariables.objects.get_table_joined_filtered(company_tidm)))

        if not existing_df.empty:
            df_new = pd.DataFrame()
            df_existing = existing_df
        else:
            df_new = new_df
            df_existing = pd.DataFrame()

        return df_new, df_existing

    def _create_rows(self, df_create):

        # Save to database
        reports = [
            DcfVariables(
                company=Companies.objects.get(id=row["company_id"]),
                parameter=Params.objects.get(id=row["parameter_id"]),
                value=row["value"],
            )
            for i, row in df_create.iterrows()
        ]
        list_of_objects = DcfVariables.objects.bulk_create(reports)

        total_rows_added = len(list_of_objects)

        return total_rows_added

    def _update_rows(self, df_update, company_tidm):

        extsting_qs = DcfVariables.objects.filter(company__tidm=company_tidm)

        num_rows_updated = DcfVariables.objects.bulk_update(
            extsting_qs, ["value"]
        )

        return num_rows_updated
