from django.core.management.base import BaseCommand
from ancillary_info.models import Companies, Params, ParamsApi
from financial_reports.models import FinancialReports
from api_import.vendors.alpha_vantage.client import AlphaVantageClient
import pandas as pd
from time import sleep


class Command(BaseCommand):
    help = "Imports Financial Data From Alpha Vantage API"

    def add_arguments(self, parser):
        parser.add_argument("--symbol", nargs="+", type=str)

    def handle(self, *args, **options):
        df_params_api = pd.DataFrame(list(ParamsApi.objects.get_params_api_joined()))
        df_companies = pd.DataFrame(list(Companies.objects.get_companies_joined()))

        # Specific symbols or all
        if options["symbol"] is None:
            comp_list = df_companies["tidm"].to_list()
        else:
            comp_list = options["symbol"]

        num_comps = len(comp_list)
        comp_num = 0
        api_call_num = 0
        total_rows_added = 0

        # For each report import data
        for current_company in comp_list:
            comp_num = comp_num + 1
            print(f"API Import {comp_num} of {num_comps}: {current_company}")

            # Get info oncurrent company
            comp_idx = df_companies[df_companies['tidm'] == current_company].index[0]
            curr_comp_id = df_companies["id"].iat[comp_idx]
            curr_comp_loc = df_companies["country__value"].iat[comp_idx]

            # For each statement type
            statement_list = ["INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW"]

            if curr_comp_loc == "US":

                for statement in statement_list:
                    api_call_num = api_call_num + 1

                    # Alpha Vantage limits requests to 5 every minute
                    if api_call_num % 5 == 0:
                        print("60 second delay")
                        sleep(65)

                    # AV API Share Import
                    av_import = AlphaVantageClient()
                    header, json_data = av_import.get_financial_data(
                        symbol=current_company, type=statement
                    )

                    # Convert to dataframe and unpivot
                    df_data = pd.DataFrame(json_data[header])
                    df_data = df_data.melt("fiscalDateEnding")

                    # Format dataframe to database schema
                    df_data = self._format_dataframe(df_data, curr_comp_id)

                    # Generate parameter_id and replace index
                    df_data = self._generate_param_id(df_params_api, df_data)

                    # Check datetime format
                    df_data = self._datetime_format(df_data)

                    # Filter out prices already in DB
                    latest_share_data = FinancialReports.objects.get_latest_date(
                        current_company
                    )
                    latest_date = latest_share_data.time_stamp
                    latest_date_first = latest_date.replace(day=1)
                    dates_first = (
                        df_data["time_stamp"].dt.to_period("M").dt.to_timestamp()
                    )

                    mask = dates_first > pd.Timestamp(latest_date_first)

                    df_data = df_data.loc[mask]

                    df_data["value"] = df_data["value"].replace("None", None)

                    num_rows = df_data.shape[0]

                    # Save to database
                    reports = [
                        FinancialReports(
                            company=Companies.objects.get(id=row["company_id"]),
                            parameter=Params.objects.get(id=row["parameter_id"]),
                            time_stamp=row["time_stamp"],
                            value=row["value"],
                        )
                        for i, row in df_data.iterrows()
                    ]
                    FinancialReports.objects.bulk_create(reports)

                    print(f"Rows saved to database: {num_rows} for {statement}")

                total_rows_added = total_rows_added + num_rows

        print(f"{total_rows_added} saved to database")

        return str(total_rows_added)

    def _format_dataframe(self, df, company_id):
        df.insert(0, "company_id", [company_id] * df.shape[0])
        df.reset_index(drop=True, inplace=True)
        df.rename(
            columns={
                "fiscalDateEnding": "time_stamp",
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

    @staticmethod
    def _generate_param_id(df_params_api, df_data):

        param_id_list = []

        param_name_list = df_params_api["param_name_api"].tolist()
        param_id_list = df_params_api["param__id"].tolist()

        # Replace index with id
        df_data = df_data.reset_index()
        df_data["index_id"] = df_data["variable"].replace(
            param_name_list, param_id_list
        )

        # Filter out rows not in params list
        df_data = df_data[df_data["variable"].isin(param_name_list)]
        df_data = df_data.rename(columns={"index_id": "parameter_id"})
        df_data.drop(["variable"], axis=1, inplace=True)

        return df_data
