import pandas as pd

from .csv_import import import_ancillary_csv
from .ancillary_objects import (
    Markets,
    CompanyType,
    IndustryRisk,
    ReportType,
    Industries,
    ReportSection,
    Params,
    CalcVariables,
    Companies,
)

from ..common.mysql_base import session_factory, engine


class AncillaryInfo:
    def __init__(self):
        session_factory()

    def populate_tables(self):
        table_list = [
            Markets,
            CompanyType,
            IndustryRisk,
            ReportType,
            Industries,
            ReportSection,
            Params,
            CalcVariables,
            Companies,
        ]

        for table_object in table_list:
            table_name = table_object.__tablename__
            df = import_ancillary_csv(table_object)

            df.to_sql(
                table_name, engine, if_exists="append", index=False, chunksize=500
            )

    def get_markets(self):
        session = session_factory()
        query = session.query(Markets)
        table_df = pd.read_sql(query.statement, query.session.bind)

        return table_df

    def get_company_types(self):
        table_df = pd.read_sql_table(CompanyType.__tablename__, con=engine)
        return table_df

    def get_industry_risks(self):
        table_df = pd.read_sql_table(IndustryRisk.__tablename__, con=engine)
        return table_df

    def get_report_types(self):
        table_df = pd.read_sql_table(ReportType.__tablename__, con=engine)
        return table_df

    def get_industries(self):
        table_df = pd.read_sql_table(Industries.__tablename__, con=engine)
        return table_df

    def get_report_sections(self):
        table_df = pd.read_sql_table(ReportSection.__tablename__, con=engine)
        return table_df

    def get_params(self):
        table_df = pd.read_sql_table(Params.__tablename__, con=engine)
        return table_df

    def get_params_joined(self):
        session = session_factory()
        query = (
            session.query(Params)
            .join(ReportSection)
            .join(ReportType)
            .with_entities(
                Params.id,
                Params.param_name,
                Params.limit_logic,
                Params.limit_value,
                Params.param_description,
                ReportSection.report_section,
                ReportSection.report_section_last,
                ReportType.report_name,
            )
        )

        table_df = pd.read_sql(query.statement, query.session.bind)

        return table_df

    def get_calc_vars(self):
        table_df = pd.read_sql_table(CalcVariables.__tablename__, con=engine)
        return table_df

    def get_calc_vars_joined(self):
        session = session_factory()
        query = (
            session.query(CalcVariables)
            .join(Params)
            .with_entities(
                Params.param_name,
                CalcVariables.value,
            )
        )

        table_df = pd.read_sql(query.statement, query.session.bind)

        return table_df

    def get_companies(self):
        table_df = pd.read_sql_table(Companies.__tablename__, con=engine)

        return table_df

    def get_companies_joined(self):
        session = session_factory()
        query = (
            session.query(Companies)
            .join(Markets)
            .join(Industries)
            .join(CompanyType)
            .with_entities(
                Companies.id,
                Companies.tidm,
                Companies.company_name,
                Companies.company_summary,
                Industries.industry_name,
                CompanyType.company_type,
                Markets.share_listing,
            )
        )

        table_df = pd.read_sql(query.statement, query.session.bind)

        return table_df
