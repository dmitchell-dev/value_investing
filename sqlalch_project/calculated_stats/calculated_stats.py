import pandas as pd

from ..ancillary_info.ancillary_info import AncillaryInfo
from .calculated_stats_objects import CalculatedStatsObjects
from ..share_prices.share_price import SharePrice
from ..financial_reports.financial import Financial
from ..common.mysql_base import session_factory, engine

from ..ancillary_info.ancillary_objects import (
    Companies,
    Parameters
    )

from .manager import (
    debt_to_ratio,
    current_ratio,
    return_on_equity,
    equity_per_share,
    price_per_earnings,
    price_book_value,
    annual_yield,
    fcf_growth_rate,
    div_payment,
    dcf_intrinsic_value,
    share_price,
    revenue_growth,
    eps_growth,
    dividend_growth,
    growth_quality,
    revenue_growth_10_year,
    earnings_growth_10_year,
    dividend_growth_10_year,
    overall_growth_and_rate,
    capital_employed,
    roce,
    median_roce_10_year,
    debt_ratio,
    pe_10_year,
    dp_10_year,
)


class CalculatedStats:
    def __init__(self):
        session_factory()

    def populate_tables(self):
        # Get ancillary data
        df_companies = AncillaryInfo().get_companies_joined()
        df_params = AncillaryInfo().get_parameters_joined()
        df_dcf_variables = AncillaryInfo().get_calc_vars_joined()

        # Calculate values for each company
        # Get list of companies
        company_list = df_companies.tidm.to_list()
        num_companies = len(company_list)
        company_num = 0

        for company_tidm in company_list:
            company_num = company_num + 1
            print(f"Company {company_num} of {num_companies}, {company_tidm}")

            # Get Share Price
            share_price_instance = SharePrice()
            df_share_price = share_price_instance.get_share_joined_filtered(
                company_tidm
            )

            # Get Financial Data
            financial_instance = Financial()
            df = financial_instance.get_financial_data_joined_filtered(company_tidm)
            df["param_name_report_section"] = (
                df["param_name"] + "_" + df["report_section"]
            )
            df_pivot = df.pivot(
                columns="time_stamp",
                index="param_name_report_section",
                values="value"
            )
            df_pivot = df_pivot.astype(float)

            # Calculations
            calc_list = []

            # Debt to Equity (D/E) =
            # Balance Sheet Total liabilities_Liabilities
            # / Total equity_Equity
            df_d_e = debt_to_ratio(df_pivot)
            calc_list.append(df_d_e)

            # Current Ratio =
            # Current assets_Assets
            # / Current liabilities_Liabilities
            df_cr = current_ratio(df_pivot)
            calc_list.append(df_cr)

            # Return on Equity (ROE) =
            # Profit for financial year_Continuous Operatings
            # / Shareholders funds (NAV)_Equity
            df_roe = return_on_equity(df_pivot)
            calc_list.append(df_roe)

            # Equity (Book Value) Per Share =
            # Shareholders funds (NAV)_Equity
            # / Average shares (diluted)_Other
            df_eps = equity_per_share(df_pivot)
            calc_list.append(df_eps)

            # Price to Earnings (P/E) =
            # Market capitalisation_Other
            # / Profit for financial year_Continuous Operatings
            df_ppe = price_per_earnings(df_pivot)
            calc_list.append(df_ppe)

            # Price to Book Value (Equity) =
            # Market capitalisation_Other
            # / Average shares (diluted)_Other
            df_pbv = price_book_value(df_pivot, df_eps)
            calc_list.append(df_pbv)

            # Annual Yield (Return) =
            # Profit for financial year_Continuous Operatings
            # / Market capitalisation_Other
            df_a_return = annual_yield(df_pivot)
            calc_list.append(df_a_return)

            # FCF Growth Rate
            # FCF Growth Rate = Free cash flow (FCF)_Free Cash Flow
            df_fcf_gr, df_fcf = fcf_growth_rate(df_pivot)
            calc_list.append(df_fcf_gr)

            # Dividend Payment
            # Dividend Payment = if there has been dividend payment
            df_div_payment = div_payment(df_pivot)
            calc_list.append(df_div_payment)

            # Dividend Cover
            # TODO

            # Calculate DCF Intrinsic Value
            df_dcf_intrinsic_value = dcf_intrinsic_value(
                df_pivot, df_dcf_variables
                 )
            calc_list.append(df_dcf_intrinsic_value)

            # Share Price
            df_share_price_reduced = share_price(df_fcf, df_share_price)
            calc_list.append(df_share_price_reduced)

            # Revenue Growth
            df_revenue_growth = revenue_growth(df_pivot)
            calc_list.append(df_revenue_growth)

            # EPS Growth
            df_eps_growth = eps_growth(df_pivot)
            calc_list.append(df_eps_growth)

            # Dividend Growth
            df_div_growth = dividend_growth(df_pivot)
            calc_list.append(df_div_growth)

            # Growth Quality
            df_growth_quality = growth_quality(
                df_pivot, df_revenue_growth, df_eps_growth, df_div_growth
            )
            calc_list.append(df_growth_quality)

            # Revenue Growth (10 year)
            df_rev_growth_10 = revenue_growth_10_year(df_pivot)
            calc_list.append(df_rev_growth_10)

            # Earnings Growth (10 year)
            df_eps_growth_10 = earnings_growth_10_year(df_pivot)
            calc_list.append(df_eps_growth_10)

            # Dividend Growth (10 year)
            df_div_growth_10 = dividend_growth_10_year(df_pivot)
            calc_list.append(df_div_growth_10)

            # Overall Growth (10 year) &
            # Growth Rate (10 year)
            df_overall_growth, df_growth_rate = overall_growth_and_rate(
                df_pivot, df_rev_growth_10, df_eps_growth_10, df_div_growth_10
            )
            calc_list.append(df_overall_growth)
            calc_list.append(df_growth_rate)

            # Capital Employed
            df_ce = capital_employed(df_pivot)
            calc_list.append(df_ce)

            # ROCE
            df_roce = roce(df_pivot, df_ce)
            calc_list.append(df_roce)

            # Median ROCE (10 year)
            df_roce_median = median_roce_10_year(df_pivot, df_roce)
            calc_list.append(df_roce_median)

            # Debt Ratio
            df_debt_ratio = debt_ratio(df_pivot)
            calc_list.append(df_debt_ratio)

            # Fill in the missing dates for share price
            df_calculated = pd.concat(calc_list)

            # PE10
            df_pe10 = pe_10_year(df_pivot, df_calculated)
            calc_list.append(df_pe10)

            # DP10
            df_dp10 = dp_10_year(df_pivot, df_calculated)
            calc_list.append(df_dp10)

            # Merge all dataframes
            df_calculated = pd.concat(calc_list)

            # if company_tidm == 'BRBY':
            #     print(df_calculated)
            #     print('STOP')

            # Generate parameter_id and replace index
            df_unpivot = self._replace_with_id(
                df_calculated,
                company_tidm,
                df_params,
                df_companies
                )

            # Check datetime format
            df_unpivot = self._datetime_format(df_unpivot)

            # Replace infinity values
            df_unpivot['value'] = df_unpivot['value'].astype(str)
            df_unpivot['value'] = df_unpivot['value'].replace(
                ["inf", "-inf"], None
            )

            # Populate database
            df_unpivot.to_sql(
                CalculatedStatsObjects.__tablename__,
                con=engine,
                if_exists="append",
                index=False,
            )

    def get_table_joined_filtered(self, rank_type):
        session = session_factory()
        query = (
            session.query(CalculatedStatsObjects)
            .join(Companies)
            .join(Parameters)
            .with_entities(
                CalculatedStatsObjects.time_stamp,
                CalculatedStatsObjects.value,
                Companies.tidm,
                Parameters.param_name,
            )
            .filter(Parameters.param_name == rank_type)
        )

        table_df = pd.read_sql(query.statement, query.session.bind)

        return table_df

    def _replace_with_id(self, df_calculated, company_tidm, df_params, df_companies):
        param_id_list = []
        param_list = df_calculated.index
        for param in param_list:

            param_id = df_params[df_params.param_name == param].id.values[0]
            param_id_list.append(param_id)

        df_calculated.index = param_id_list

        # company id
        company_id = df_companies[
            df_companies["tidm"] == company_tidm
        ].id.values[0]

        df_unpivot = pd.melt(
            df_calculated,
            var_name="time_stamp",
            value_name="value",
            ignore_index=False
        )

        df_unpivot['company_id'] = company_id
        df_unpivot["parameter_id"] = df_unpivot.index

        return df_unpivot

    def _datetime_format(self, df):
        date_fmts = ("%d/%m/%y", "%d/%m/%Y")
        for fmt in date_fmts:
            try:
                df["time_stamp"] = pd.to_datetime(
                    df["time_stamp"], format=fmt
                )
                break
            except ValueError:
                pass

        return df
