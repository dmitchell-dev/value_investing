import pandas as pd
from django.core.management.base import BaseCommand
from ancillary_info.models import (
    Params,
    Companies,
)
from share_prices.models import SharePrices
from financial_reports.models import FinancialReports
from calculated_stats.models import CalculatedStats

from calculated_stats.managers import (
    total_equity,
    shares_outstanding,
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
    annual_yield,
    div_payment,
    div_cover,
    dcf_intrinsic_value,
    roce,
    debt_ratio,
)


class Command(BaseCommand):
    help = "Calculates Stats from Financial Reports"

    def handle(self, *args, **kwargs):
        # Get ancillary data
        df_params = pd.DataFrame(list(Params.objects.get_params_joined()))
        df_companies = pd.DataFrame(list(Companies.objects.get_companies_joined()))
        #df_dcf_variables = pd.DataFrame(
        #    list(CalcVariables.objects.get_calc_vars_joined())
        #)

        # Calculate values for each company
        # Get list of companies
        company_list = df_companies.tidm.to_list()
        num_companies = len(company_list)
        company_num = 0

        for company_tidm in company_list:
            company_num = company_num + 1
            print(f"Company {company_num} of {num_companies}, {company_tidm}")

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

            df_s_o = shares_outstanding(df_pivot)
            calc_list.append(df_s_o)

            df_share_price_reduced = share_price(df_pivot, df_share_price)
            calc_list.append(df_share_price_reduced)

            df_m_c = market_cap(df_s_o, df_share_price_reduced)
            calc_list.append(df_m_c)

            df_e_v = enterprise_value(df_pivot, df_m_c)
            calc_list.append(df_e_v)

            df_fcf = free_cash_flow(df_pivot)
            calc_list.append(df_fcf)

            df_c_e = capital_employed(df_pivot)
            calc_list.append(df_c_e)

            df_dps = dividends_per_share(df_pivot, df_s_o)
            calc_list.append(df_dps)

            df_d_e = debt_to_eq_ratio(df_pivot, df_t_e)
            calc_list.append(df_d_e)

            df_cr = current_ratio(df_pivot)
            calc_list.append(df_cr)

            df_roe = return_on_equity(df_pivot, df_t_e)
            calc_list.append(df_roe)

            df_eps = equity_per_share(df_t_e, df_s_o)
            calc_list.append(df_eps)

            df_ppe = price_per_earnings(df_pivot, df_m_c)
            calc_list.append(df_ppe)

            df_pbv = price_book_value(df_m_c, df_s_o, df_eps)
            calc_list.append(df_pbv)

            df_a_return = annual_yield(df_pivot, df_e_v)
            calc_list.append(df_a_return)

            df_div_payment = div_payment(df_dps)
            calc_list.append(df_div_payment)

            df_div_cover = div_cover(df_pivot)
            calc_list.append(df_div_cover)

            df_dcf_intrinsic_value = dcf_intrinsic_value(df_pivot, df_dcf_variables)
            calc_list.append(df_dcf_intrinsic_value)

            # ROCE
            df_roce = roce(df_pivot, df_c_e)
            calc_list.append(df_roce)

            # Debt Ratio
            df_debt_ratio = debt_ratio(df_pivot)
            calc_list.append(df_debt_ratio)

            # Fill in the missing dates for share price
            df_calculated = pd.concat(calc_list)

            # Merge all dataframes
            df_calculated = pd.concat(calc_list)

            # if company_tidm == 'BRBY':
            #     print(df_calculated)
            #     print('STOP')

            # Generate parameter_id and replace index
            df_unpivot = self._replace_with_id(
                df_calculated, company_tidm, df_params, df_companies
            )

            # Check datetime format
            df_unpivot = self._datetime_format(df_unpivot)

            # Replace infinity values
            df_unpivot["value"] = df_unpivot["value"].astype(str)
            df_unpivot["value"] = df_unpivot["value"].replace(["inf", "-inf"], None)

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
        date_fmts = ("%d/%m/%y", "%d/%m/%Y")
        for fmt in date_fmts:
            try:
                df["time_stamp"] = pd.to_datetime(df["time_stamp"], format=fmt)
                break
            except ValueError:
                pass

        return df
