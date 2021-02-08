import pandas as pd
import os


def import_share_price_csv(current_company_filename):
    # Get company report data
    df = pd.read_csv(f"data/share_prices/{current_company_filename}")
    df = df.where((pd.notnull(df)), None)

    return df


def get_share_list():
    # Import each file, process and save to database
    # Get list of reports
    path = "data/share_prices"
    file_list = []
    for files in os.listdir(path):
        file_list.append(files)

    return file_list
