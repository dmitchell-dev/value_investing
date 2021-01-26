import pandas as pd


def import_ancillary_csv(table_object):
    table_name = table_object.__tablename__
    df = pd.read_csv(f"data/database_tables/{table_name}.csv")

    return df
