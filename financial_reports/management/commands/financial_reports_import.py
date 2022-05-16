from django.core.management.base import BaseCommand
from financial_reports.models import FinancialReports
from ancillary_info.models import Params, Companies
import pandas as pd
import os


class Command(BaseCommand):
    help = "Populates Static tables from csv files"

    def handle(self, *args, **kwargs):
        print("Import Reports")
        df_params = pd.DataFrame(list(Params.objects.get_params_joined()))
        df_companies = pd.DataFrame(list(Companies.objects.get_companies_joined()))

        file_list = self._get_report_list()
        num_files = len(file_list)
        file_num = 0

        # For each report import data
        for current_company_filename in file_list:
            file_num = file_num + 1
            s = f"file {file_num} of {num_files}, {current_company_filename}"
            print(s)

            # Process filename
            current_company_tidm, report_section_last_list = self._process_filename(
                current_company_filename, df_params
            )

            # Get company report data
            df_data = self._import_financial_csv(current_company_filename)

            # Generate parameter_id and replace index
            df_data = self._generate_param_id(
                df_params, df_data, report_section_last_list
            )

            # company id
            company_id = df_companies[
                df_companies["tidm"] == current_company_tidm
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

            # Replace infinity values
            df_unpivot["value"] = df_unpivot["value"].replace(
                ["Infinity", "-Infinity"], None
            )

            # Check datetime format
            df_unpivot = self._datetime_format(df_unpivot)

            # Populate database
            reports = [
                FinancialReports(
                    company=Companies.objects.get(id=row["company_id"]),
                    parameter=Params.objects.get(id=row["parameter_id"]),
                    time_stamp=row["time_stamp"],
                    value=row["value"],
                )
                for i, row in df_unpivot.iterrows()
            ]
            FinancialReports.objects.bulk_create(reports)

    @staticmethod
    def _import_financial_csv(current_company_filename):
        df = pd.read_csv(
            f"data/company_reports/{current_company_filename}",
            index_col="Period Ending",
            skiprows=1,
        )

        df = df.where((pd.notnull(df)), None)
        df = df.drop("Result Type", axis=0)
        if " " in df.index:
            df = df.drop(" ")

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
    def _process_filename(current_company_filename, df_params):
        # Get current report type
        filename_first = current_company_filename.split("_")[2]
        filename_second = current_company_filename.replace(".csv", "").split("_")[3]
        current_report_type = f"{filename_first} {filename_second}"

        # Get company tidm for associated id
        current_company_tidm = current_company_filename.split("_")[1]

        # Get last param name in section
        report_section_last_df = df_params[
            df_params.report_section__report_type__report_name
            == current_report_type.title()
        ]
        report_section_last_df = report_section_last_df[
            "report_section__report_section_last"
        ].unique()
        report_section_last_list = report_section_last_df.tolist()

        return (current_company_tidm, report_section_last_list)

    @staticmethod
    def _generate_param_id(df_params, df_data, report_section_last_list):
        i_section = 0
        i_param = 0
        param_id_list = []

        param_list = df_data.index

        for section in report_section_last_list:

            param_section_filter_list_df = df_params[
                df_params.report_section__report_section_last == section
            ]

            while True:

                param_id = param_section_filter_list_df[
                    (param_section_filter_list_df.param_name == param_list[i_param])
                ]
                param_id = param_id.iloc[0]["id"]
                param_id_list.append(param_id)

                if param_list[i_param] == section:
                    i_section = i_section + 1
                    i_param = i_param + 1
                    break

                i_param = i_param + 1

        df_data.index = param_id_list

        return df_data

    @staticmethod
    def _datetime_format(df):
        date_fmts = ("%d/%m/%y", "%d/%m/%Y")
        for fmt in date_fmts:
            try:
                df["time_stamp"] = pd.to_datetime(df["time_stamp"], format=fmt)
                break
            except ValueError:
                pass

        return df
