import pandas as pd

from sqlalch_project.ancillary_info.ancillary_info import AncillaryInfo
from .csv_import import get_report_list
from .financial_objects import FinancialObjects

from ..common.mysql_base import session_factory, engine


class Financial:
    def __init__(self):
        session_factory()

    def populate_tables(self):
        # Import anciliary tables
        df_params = AncillaryInfo().get_parameters_joined()
        df_companies = AncillaryInfo().get_companies_joined()
        df_dcf_variables = AncillaryInfo().get_calc_vars()

        file_list = get_report_list()
        num_files = len(file_list)
        file_num = 0

        # For each report import data
        for current_company_filename in file_list:
            file_num = file_num + 1
            s = f"file {file_num} of {num_files}, {current_company_filename}"
            print(s)

            # # Get current report type
            # filename_first = current_company_filename.split("_")[2]
            # filename_second = current_company_filename.replace(".csv", "").split("_")[3]
            # current_report_type = f"{filename_first} {filename_second}"

            # # Get company tidm for associated id
            # current_company_tidm = current_company_filename.split("_")[1]

            # # Get last param name in section
            # report_section_last_df = self.df_params[
            #     self.df_params.report_name == current_report_type.title()
            # ]
            # report_section_last_df = report_section_last_df[
            #     "report_section_last"
            # ].unique()
            # report_section_last_list = report_section_last_df.tolist()

            current_company_tidm, report_section_last_list = self._report_data(current_company_filename, df_params)

            # Get company report data
            df_data = pd.read_csv(
                f"data/company_reports/{current_company_filename}",
                index_col="Period Ending",
                skiprows=1,
            )
            df_data = df_data.where((pd.notnull(df_data)), None)
            df_data = df_data.drop("Result Type", axis=0)
            if " " in df_data.index:
                df_data = df_data.drop(" ")

            # Generate parameter_id and replace index
            i_section = 0
            i_param = 0
            param_id_list = []

            param_list = df_data.index


    def get_financial_data(self):
        table_df = pd.read_sql_table(
            FinancialObjects.__tablename__,
            con=engine
        )
        return table_df

    def _report_data(self,current_company_filename, df_params):
        # Get current report type
        filename_first = current_company_filename.split("_")[2]
        filename_second = current_company_filename.replace(".csv", "").split("_")[3]
        current_report_type = f"{filename_first} {filename_second}"

        # Get company tidm for associated id
        current_company_tidm = current_company_filename.split("_")[1]

        # Get last param name in section
        report_section_last_df = df_params[
            df_params.report_name == current_report_type.title()
        ]
        report_section_last_df = report_section_last_df[
            "report_section_last"
        ].unique()
        report_section_last_list = report_section_last_df.tolist()

        return (current_company_tidm, report_section_last_list)
