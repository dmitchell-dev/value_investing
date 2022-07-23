import pandas as pd
from django.core.management.base import BaseCommand
from ancillary_info.models import (
    Params,
    Companies,
)
from share_prices.models import SharePrices
from financial_reports.models import FinancialReports
from calculated_stats.models import CalculatedStats, DcfVariables

from calculated_stats.managers import (
    total_equity,
    share_price,
    market_cap,
    enterprise_value,
    free_cash_flow,
    capital_employed,
    dividends_per_share,
    debt_to_eq_ratio,
    current_ratio,
    return_on_equity,
    equity_per_share,
    price_per_earnings,
    price_book_value,
    earnings_yield,
    annual_yield,
    div_cover,
    dcf_intrinsic_value,
    roce,
    margin_of_safety,
)


class Command(BaseCommand):
    help = "Calculates Stats from Financial Reports"

    def add_arguments(self, parser):
        parser.add_argument("--symbol", nargs="+", type=str)

    def handle(self, *args, **options):
        # Get ancillary data
        df_params = pd.DataFrame(list(Params.objects.get_params_joined()))
        df_companies = pd.DataFrame(list(Companies.objects.get_companies_joined()))

        # Specific symbols or all
        if options["symbol"] is None:
            comp_list = df_companies["tidm"].to_list()
        else:
            comp_list = options["symbol"]

        # Calculate values for each company
        # Get list of companies
        num_companies = len(comp_list)
        company_num = 0
        total_rows_added = 0

        for company_tidm in comp_list:
            company_num = company_num + 1
            print(f"Company {company_num} of {num_companies}, {company_tidm}")

            # Get DCF Variables
            df_dcf_variables = pd.DataFrame(
                list(DcfVariables.objects.get_table_joined_filtered(company_tidm))
            )

            # Get Share Price
            df_share_price = pd.DataFrame(
                list(SharePrices.objects.get_share_joined_filtered(company_tidm))
            )

            # Get Financial Data
            df = pd.DataFrame(
                list(
                    FinancialReports.objects.get_financial_data_joined_filtered(
                        company_tidm
                    )
                )
            )

            df_pivot = df.pivot(
                columns="time_stamp",
                index="parameter__param_name",
                values="value",
            )
            df_pivot = df_pivot.astype(float)

            # Calculations
            calc_list = []

            df_t_e = total_equity(df_pivot)
            calc_list.append(df_t_e)

            df_share_price_reduced = share_price(df_pivot, df_share_price)
            calc_list.append(df_share_price_reduced)

            df_m_c = market_cap(df_pivot, df_share_price_reduced)
            calc_list.append(df_m_c)

            df_e_v = enterprise_value(df_pivot, df_m_c)
            calc_list.append(df_e_v)

            df_fcf = free_cash_flow(df_pivot)
            calc_list.append(df_fcf)

            df_c_e = capital_employed(df_pivot)
            calc_list.append(df_c_e)

            df_dps = dividends_per_share(df_pivot)
            calc_list.append(df_dps)

            df_d_e = debt_to_eq_ratio(df_pivot, df_t_e)
            calc_list.append(df_d_e)

            df_cr = current_ratio(df_pivot)
            calc_list.append(df_cr)

            df_roe = return_on_equity(df_pivot, df_t_e)
            calc_list.append(df_roe)

            df_eps = equity_per_share(df_pivot, df_t_e)
            calc_list.append(df_eps)

            df_ppe = price_per_earnings(df_pivot, df_m_c)
            calc_list.append(df_ppe)

            df_pbv = price_book_value(df_pivot, df_m_c, df_eps)
            calc_list.append(df_pbv)

            df_e_yield = earnings_yield(df_pivot, df_e_v)
            calc_list.append(df_e_yield)

            df_a_yield = annual_yield(df_pivot, df_m_c)
            calc_list.append(df_a_yield)

            df_div_cover = div_cover(df_pivot)
            calc_list.append(df_div_cover)

            df_dcf_intrinsic_value = dcf_intrinsic_value(
                df_pivot, df_dcf_variables, df_fcf
            )
            calc_list.append(df_dcf_intrinsic_value)

            # ROCE
            df_roce = roce(df_pivot, df_c_e)
            calc_list.append(df_roce)

            # Debt Ratio
            df_margin_of_safety = margin_of_safety(
                df_share_price_reduced, df_dcf_intrinsic_value
            )
            calc_list.append(df_margin_of_safety)

            # Merge all dataframes
            df_calculated = pd.concat(calc_list)

            df_calculated = df_calculated.round(decimals=2)

            # Generate parameter_id and replace index

            df_unpivot = self._replace_with_id(
                df_calculated, company_tidm, df_params, df_companies
            )

            # Check datetime format
            df_unpivot = self._datetime_format(df_unpivot)

            # Replace infinity values
            df_unpivot["value"] = df_unpivot["value"].astype(str)
            df_unpivot["value"] = df_unpivot["value"].replace(["inf", "-inf"], None)

            # Filter out prices already in DB
            latest_data = CalculatedStats.objects.get_latest_date(company_tidm)
            if latest_data:
                latest_date = latest_data.time_stamp
                mask = df_unpivot["time_stamp"] > pd.Timestamp(latest_date)
                df_unpivot = df_unpivot.loc[mask]

            num_rows = df_unpivot.shape[0]

            # Save to database
            reports = [
                CalculatedStats(
                    company=Companies.objects.get(id=row["company_id"]),
                    parameter=Params.objects.get(id=row["parameter_id"]),
                    time_stamp=row["time_stamp"],
                    value=row["value"],
                )
                for i, row in df_unpivot.iterrows()
            ]
            CalculatedStats.objects.bulk_create(reports)

            print(f"Rows saved to database: {num_rows}")

            total_rows_added = total_rows_added + num_rows

        print(f"{total_rows_added} saved to database")

        return f"Created: {str(total_rows_added)}"

    def _replace_with_id(self, df_calculated, company_tidm, df_params, df_companies):
        param_id_list = []
        param_list = df_calculated.index
        for param in param_list:

            param_id = df_params[df_params.param_name == param].id.values[0]
            param_id_list.append(param_id)

        df_calculated.index = param_id_list

        # company id
        company_id = df_companies[df_companies["tidm"] == company_tidm].id.values[0]

        df_unpivot = pd.melt(
            df_calculated, var_name="time_stamp", value_name="value", ignore_index=False
        )

        df_unpivot["company_id"] = company_id
        df_unpivot["parameter_id"] = df_unpivot.index

        return df_unpivot

    def _datetime_format(self, df):
        date_fmts = ("%Y-%m-%d", "%d/%m/%y", "%d/%m/%Y")
        for fmt in date_fmts:
            try:
                df["time_stamp"] = pd.to_datetime(df["time_stamp"], format=fmt)
                break
            except ValueError:
                pass

        return df
