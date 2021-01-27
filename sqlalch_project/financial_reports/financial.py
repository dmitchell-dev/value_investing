import pandas as pd

from sqlalch_project.ancillary_info.ancillary_info import AncillaryInfo
from .csv_import import get_report_list, import_financial_csv
from .financial_objects import FinancialObjects

from ..common.mysql_base import session_factory, engine

from ..ancillary_info.ancillary_objects import Companies, Parameters, ReportSection


class Financial:
    def __init__(self):
        session_factory()

    def populate_tables(self):
        # Import anciliary tables
        df_params = AncillaryInfo().get_parameters_joined()
        df_companies = AncillaryInfo().get_companies_joined()

        file_list = get_report_list()
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
            df_data = import_financial_csv(current_company_filename)

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
            df_unpivot = self._datetime_format(self, df_unpivot)

            # Populate database
            df_unpivot.to_sql(
                FinancialObjects.__tablename__,
                con=engine,
                if_exists="append",
                index=False,
            )

    def get_financial_data(self):
        table_df = pd.read_sql_table(
            FinancialObjects.__tablename__,
            con=engine
            )
        return table_df

    def get_financial_data_joined_filtered(self, tidm):
        session = session_factory()
        query = (
            session.query(FinancialObjects)
            .join(Companies)
            .join(Parameters)
            .join(ReportSection)
            .with_entities(
                Parameters.param_name,
                ReportSection.report_section,
                FinancialObjects.time_stamp,
                FinancialObjects.value,
            )
            .filter(Companies.tidm == tidm)
        )

        table_df = pd.read_sql(query.statement, query.session.bind)

        return table_df

    def _process_filename(self, current_company_filename, df_params):
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
        report_section_last_df = report_section_last_df["report_section_last"].unique()
        report_section_last_list = report_section_last_df.tolist()

        return (current_company_tidm, report_section_last_list)

    def _generate_param_id(self, df_params, df_data, report_section_last_list):
        i_section = 0
        i_param = 0
        param_id_list = []

        param_list = df_data.index

        for section in report_section_last_list:

            param_section_filter_list_df = df_params[
                df_params.report_section_last == section
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

    def _datetime_format(self, df):
        date_fmts = ("%d/%m/%y", "%d/%m/%Y")
        for fmt in date_fmts:
            try:
                df["time_stamp"] = pd.to_datetime(
                    df["time_stamp"], format=fmt
                )
                break
            except ValueError:
                pass

        return df
