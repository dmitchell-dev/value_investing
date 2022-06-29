from django.core.management.base import BaseCommand
from ancillary_info.models import Companies
from share_prices.models import SharePrices, ShareSplits
import pandas as pd


class Command(BaseCommand):
    help = "Calculates Stock Splits for each company"

    def add_arguments(self, parser):
        parser.add_argument("--symbol", nargs="+", type=str)

    def handle(self, *args, **options):
        df_companies = pd.DataFrame(list(
            Companies.objects.get_companies_joined()
            ))

        # Specific symbols or all
        if options["symbol"] is None:
            comp_list = df_companies["tidm"].to_list()
        else:
            comp_list = options["symbol"]

        num_comps = len(comp_list)
        comp_num = 0
        total_rows_added = 0
        num_rows = 0

        # For each report import data
        for current_company in comp_list:
            comp_num = comp_num + 1

            print(f"API Import {comp_num} of {num_comps}: {current_company}")

            # Get info oncurrent company
            curr_comp_id = df_companies["id"].iat[comp_num - 1]

            df_data = pd.DataFrame(list(
                SharePrices.objects.get_share_joined_filtered(current_company)
                ))

            # TODO Calculate stock Split
            df_data['share_split'] = df_data['value'].div(
                df_data['value_adjusted']
                ).diff().abs()
            df_data['share_multiple_original'] = df_data['value'].div(
                df_data['value_adjusted']
                ).abs()

            df_data_index = df_data["share_split"] > 0.1

            df_data_filtered = df_data[df_data_index]

            if not df_data_filtered.empty:

                # Filter out prices already in DB
                latest_share_data = ShareSplits.objects.get_latest_date(
                    current_company
                    )

                df_data_filtered.insert(
                    0,
                    "company_id",
                    [curr_comp_id] * df_data_filtered.shape[0]
                    )

                if latest_share_data:
                    latest_date = latest_share_data.time_stamp
                    mask = df_data_filtered["time_stamp"] > pd.Timestamp(
                        latest_date
                        )
                    df_data_filtered = df_data_filtered.loc[mask]

                num_rows = df_data_filtered.shape[0]

                # Save to database
                reports = [
                    ShareSplits(
                        company=Companies.objects.get(id=row["company_id"]),
                        time_stamp=row["time_stamp"],
                        value=row["share_split"],
                    )
                    for i, row in df_data_filtered.iterrows()
                ]
                ShareSplits.objects.bulk_create(reports)

            print(f"Rows saved to database: {num_rows}")

            total_rows_added = total_rows_added + num_rows

        print(f"{total_rows_added} saved to database")

    def _format_dataframe(self, df, company_id):
        df.insert(0, "company_id", [company_id] * df.shape[0])
        df = df.drop(
            ["1. open", "2. high", "3. low", "7. dividend amount"],
            axis=1
            )
        df["time_stamp"] = df.index
        df.reset_index(drop=True, inplace=True)
        df.rename(
            columns={
                "4. close": "value",
                "5. adjusted close": "value_adjusted",
                "6. volume": "volume",

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
