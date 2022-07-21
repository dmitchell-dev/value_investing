# import csv
# from django.conf import settings
from django.core.management.base import BaseCommand
from ancillary_info.models import (
    Params,
    Companies,
)
from calculated_stats.models import DcfVariables

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
        total_rows_added = 0
        company_num = 0
        num_rows = 0

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

            num_rows = df_data.shape[0]

            # Save to database
            reports = [
                DcfVariables(
                    company=Companies.objects.get(id=row["company_id"]),
                    parameter=Params.objects.get(id=row["parameter_id"]),
                    value=row["value"],
                )
                for i, row in df_data.iterrows()
            ]
            DcfVariables.objects.bulk_create(reports)

            print(f"Rows saved to database: {num_rows} for {company_tidm}")

            total_rows_added = total_rows_added + num_rows

            return total_rows_added

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
