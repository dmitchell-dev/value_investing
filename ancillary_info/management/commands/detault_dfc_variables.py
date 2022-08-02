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

        dcf_value_list = list(dcf_dict.values())

        # Get ancillary data
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

        for company_tidm in comp_list:
            company_num = company_num + 1
            print(f"Company {company_num} of {num_companies}, {company_tidm}")

            # company id
            company_id = df_companies[df_companies["tidm"] == company_tidm].id.values[0]

            data_dict = {
                "company_id": [company_id],
                "est_growth_rate": [dcf_value_list[0]],
                "est_disc_rate": [dcf_value_list[1]],
                "est_ltg_rate": [dcf_value_list[2]],
            }
            df_data = pd.DataFrame(data_dict)

            # Split ready for create or update
            (df_create, df_update) = self._create_update_split(
                df_data,
                company_tidm
                )

            # Create new companies
            if not df_create.empty:
                num_rows_created = self._create_rows(df_create)
                print(f"Default DCF Import Create Complete: {num_rows_created} rows updated")

        return f"Created: {str(num_rows_created)}, Updated: Not Implemented"

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
                est_growth_rate=row["est_growth_rate"],
                est_disc_rate=row["est_disc_rate"],
                est_ltg_rate=row["est_ltg_rate"],
            )
            for i, row in df_create.iterrows()
        ]
        list_of_objects = DcfVariables.objects.bulk_create(reports)

        total_rows_added = len(list_of_objects)

        return total_rows_added
