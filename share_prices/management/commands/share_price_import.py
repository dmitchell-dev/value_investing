from django.core.management.base import BaseCommand
from ancillary_info.models import Companies
from share_prices.models import SharePrices
import pandas as pd
import os


class Command(BaseCommand):
    help = "Calculates Stats from Financial Reports"

    def handle(self, *args, **kwargs):
        df_companies = pd.DataFrame(list(Companies.objects.get_companies_joined()))

        file_list = self.get_share_list()
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
            df_data = self.import_share_price_csv(current_company_filename)

            # Format dataframe to database schema
            df_data = self._format_dataframe(df_data, company_id)

            # Check datetime format
            df_data = self._datetime_format(df_data)

            num_rows = df_data.shape[0]

            # Save to database
            reports = [
                SharePrices(
                    company=Companies.objects.get(id=row["company_id"]),
                    time_stamp=row["time_stamp"],
                    value=row["value"],
                    volume=row["volume"],
                    adjustment=row["adjustment"],
                )
                for i, row in df_data.iterrows()
            ]
            SharePrices.objects.bulk_create(reports)

            print(f"Rows saved to database: {num_rows}")

    def import_share_price_csv(self, current_company_filename):
        # Get company report data
        df = pd.read_csv(f"data/share_prices/{current_company_filename}")
        df = df.where((pd.notnull(df)), None)

        return df

    def get_share_list(self):
        # Import each file, process and save to database
        # Get list of reports
        path = "data/share_prices"
        file_list = []
        for files in os.listdir(path):
            file_list.append(files)

        return file_list

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
                df["time_stamp"] = pd.to_datetime(df["time_stamp"], format=fmt)
                break
            except ValueError:
                pass

        return df
