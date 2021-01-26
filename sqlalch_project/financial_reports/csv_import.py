import pandas as pd
import os


def import_financial_csv(current_company_filename):
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


def get_report_list():
    # Import each file, process and save to database
    # Get list of reports
    path = "data/company_reports"
    file_list = []
    for files in os.listdir(path):
        file_list.append(files)

    return file_list
