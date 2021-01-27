import pandas as pd

from sqlalch_project.ancillary_info.ancillary_info import AncillaryInfo
from .csv_import import import_share_price_csv, get_share_list
from .share_price_objects import SharePriceObjects

from ..common.mysql_base import session_factory, engine

from ..ancillary_info.ancillary_objects import Companies

class SharePrice:
    def __init__(self):
        session_factory()

    def populate_tables(self):
        df_companies = AncillaryInfo().get_companies_joined()

        file_list = get_share_list()
        num_files = len(file_list)
        file_num = 0

        # For each report import data
        for current_company_filename in file_list:
            file_num = file_num + 1
            s = f"file {file_num} of {num_files}, {current_company_filename}"
            print(s)

            # Get company tidm for associated id
            current_company_tidm = current_company_filename.split("_")[1]

            # company id
            company_id = df_companies[
                df_companies["tidm"] == current_company_tidm
            ].id.values[0]

            # Get company report data
            df_data = import_share_price_csv(current_company_filename)

            # Format dataframe to database schema
            df_data = self._format_dataframe(df_data, company_id)

            # Check datetime format
            df_data = self._datetime_format(df_data)

            # Populate database
            df_data.to_sql(
                SharePriceObjects.__tablename__,
                con=engine,
                if_exists="append",
                index=False,
            )

    def get_share_data(self):
        table_df = pd.read_sql_table(
            SharePriceObjects.__tablename__,
            con=engine
            )
        return table_df

    def get_share_joined(self):
        session = session_factory()
        query = (
            session.query(SharePriceObjects)
            .join(Companies)
            .with_entities(
                SharePriceObjects.id,
                SharePriceObjects.time_stamp,
                SharePriceObjects.value,
                SharePriceObjects.volume,
                SharePriceObjects.adjustment,
                Companies.company_name,
                Companies.tidm
            )
        )

        table_df = pd.read_sql(query.statement, query.session.bind)

        return table_df

    def _format_dataframe(self, df, company_id):
        df.insert(0, "company_id", [company_id] * df.shape[0])
        df = df.drop(["Open", "High", "Low"], axis=1)
        df.rename(
            columns={
                "Date": "time_stamp",
                "Close": "value",
                "Volume": "volume",
                "Adjustment": "adjustment",
            },
            inplace=True,
        )

        return df

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
