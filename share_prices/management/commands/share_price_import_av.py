from django.core.management.base import BaseCommand
from ancillary_info.models import Companies
from share_prices.models import SharePrices
from api_import.vendors.alpha_vantage.client import AlphaVantageClient
import pandas as pd
from time import sleep


class Command(BaseCommand):
    help = "Imports Share Prices From Alpha Vantage API"

    def add_arguments(self, parser):
        parser.add_argument("--symbol", nargs="+", type=str)

    def handle(self, *args, **options):
        df_companies = pd.DataFrame(list(Companies.objects.get_companies_joined()))

        # Specific symbols or all
        if options["symbol"] is None:
            comp_list = df_companies["tidm"].to_list()
        else:
            comp_list = options["symbol"]

        num_comps = len(comp_list)
        comp_num = 0

        # For each report import data
        for current_company in comp_list:
            comp_num = comp_num + 1

            # Alpha Vantage limits requests to 5 every minute
            if comp_num % 5 == 0:
                print("90 second delay")
                sleep(90)

            print(f"API Import {comp_num} of {num_comps}: {current_company}")

            # Get info oncurrent company
            curr_comp_id = df_companies["id"].iat[comp_num - 1]
            curr_comp_loc = df_companies["country__value"].iat[comp_num - 1]

            # AV API Share Import
            av_import = AlphaVantageClient()
            header, json_data = av_import.get_share_data(
                location=curr_comp_loc,
                symbol=current_company,
                type="TIME_SERIES_WEEKLY",
            )

            # Convert to dataframe
            df_data = pd.DataFrame.from_dict(json_data[header], orient="index")

            # Format dataframe to database schema
            df_data = self._format_dataframe(df_data, curr_comp_id)

            # Check datetime format
            df_data = self._datetime_format(df_data)

            # Filter out prices already in DB
            latest_share_data = SharePrices.objects.get_latest_date(current_company)
            latest_date = latest_share_data.time_stamp
            mask = df_data["time_stamp"] > pd.Timestamp(latest_date)
            df_data = df_data.loc[mask]

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

    def _format_dataframe(self, df, company_id):
        df.insert(0, "company_id", [company_id] * df.shape[0])
        df = df.drop(["1. open", "2. high", "3. low"], axis=1)
        df["time_stamp"] = df.index
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
        df.sort_values(by="time_stamp", inplace=True)

        return df
