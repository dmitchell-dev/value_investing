import pandas as pd
import os


def import_financial_csv(table_object):
    table_name = table_object.__tablename__
    df = pd.read_csv(f"data/company_reports/{table_name}.csv")

    return df


def get_report_list():
    # Import each file, process and save to database
    # Get list of reports
    path = "data/company_reports"
    file_list = []
    for files in os.listdir(path):
        file_list.append(files)

    return file_list
