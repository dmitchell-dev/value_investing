from django.core.management.base import BaseCommand
from ancillary_info.models import Companies
from share_prices.models import SharePrices
from api_import.vendors.alpha_vantage.client import AlphaVantageClient
import pandas as pd
import os
from time import sleep


class Command(BaseCommand):
    help = "Calculates Stats from Financial Reports"

    def handle(self, *args, **kwargs):
        df_companies = pd.DataFrame(
            list(Companies.objects.get_companies_joined())
        )

        comp_list = df_companies['tidm'].to_list()
        num_comps = len(comp_list)
        comp_num = 0

        # For each report import data
        for current_company in comp_list:
            comp_num = comp_num + 1

            # Alpha Vantage limits requests to 5 every minute
            if comp_num % 5 == 0:
                print('60 second delay')
                sleep(60)

            print(f"file {comp_num} of {num_comps}, {current_company}")

            # AV API Share Import
            av_import = AlphaVantageClient()
            header, json_data = av_import.get_share_price(
                symbol=current_company
            )

            # Convert to dataframe
            df_data = pd.DataFrame.from_dict(
                json_data[header], orient='index'
            )

            # Format dataframe to database schema
            curr_comp_id = df_companies.iat[comp_num-1, 0]
            df_data = self._format_dataframe(df_data, curr_comp_id)

            # Check datetime format
            df_data = self._datetime_format(df_data)

            # Save to database
            reports = [
                SharePrices(
                    company=Companies.objects.get(id=row["company_id"]),
                    time_stamp=row["time_stamp"],
                    value=row["value"],
                    volume=row["volume"],
                )
                for i, row in df_data.iterrows()
            ]
            SharePrices.objects.bulk_create(reports)

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
        df = df.drop(["1. open", "2. high", "3. low"], axis=1)
        df['time_stamp'] = df.index
        df.reset_index(drop=True, inplace=True)
        df.rename(
            columns={
                "4. close": "value",
                "5. volume": "volume",
            },
            inplace=True,
        )

        return df

    def _datetime_format(self, df):
        date_fmts = ("%Y-%m-%d", "%d/%m/%y", "%d/%m/%Y")
        for fmt in date_fmts:
            try:
                df["time_stamp"] = pd.to_datetime(df["time_stamp"], format=fmt)
                break
            except ValueError:
                pass

        # Order datetimes
        df.sort_values(by='time_stamp', inplace=True)

        return df
