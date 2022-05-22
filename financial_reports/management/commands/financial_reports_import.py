from django.core.management.base import BaseCommand
from financial_reports.models import FinancialReports
from ancillary_info.models import Params, Companies, ParamsApi
import pandas as pd
import os


class Command(BaseCommand):
    help = "Populates Static tables from csv files"

    def handle(self, *args, **kwargs):
        print("Import Reports")
        df_params_api = pd.DataFrame(list(
            ParamsApi.objects.get_params_api_joined())
            )
        df_companies = pd.DataFrame(list(
            Companies.objects.get_companies_joined())
            )

        file_list = self._get_report_list()
        num_files = len(file_list)
        file_num = 0

        # For each report import data
        for current_company_filename in file_list:
            file_num = file_num + 1
            s = f"file {file_num} of {num_files}, {current_company_filename}"
            print(s)

            # Process filename
            current_company_tidm = self._process_filename(
                current_company_filename
            )

            # Get company report data
            df_data = self._import_reporting_data(current_company_filename)

            # Generate parameter_id and replace index
            df_data = self._generate_param_id(
                df_params_api, df_data
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
                df_data,
                var_name="time_stamp",
                value_name="value",
                ignore_index=False
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

        # Stack dataframes
        df = pd.concat([df_income, df_balance, df_cash], axis=0)

        # Drop empty rows with empty index
        df.drop(df[df.index.isnull()].index, inplace=True)

        # Drop last LTM Column if exists
        if 'LTM' in df.columns:
            df.drop(['LTM'], axis=1, inplace=True)

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
        current_company_tidm = current_company_filename.split("_")[0]

        return current_company_tidm

    @staticmethod
    def _generate_param_id(df_params_api, df_data):

        param_id_list = []

        param_name_list = df_params_api['param_name_api'].tolist()
        param_id_list = df_params_api['id'].tolist()

        df_data = df_data.reset_index()
        df_data['index_id'] = df_data['index'].replace(
            param_name_list,
            param_id_list
            )

        # Filter out rows not in params list
        df_index = df_data['index'].isin(param_name_list)
        df_data = df_data[df_data['index'].isin(param_name_list)]

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
