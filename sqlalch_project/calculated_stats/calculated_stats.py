import pandas as pd

from ..ancillary_info.ancillary_info import AncillaryInfo
from .calculated_stats_objects import CalculatedStatsObjects
from ..share_prices.share_price import SharePrice
from ..financial_reports.financial import Financial
from ..common.mysql_base import session_factory, engine
from ..ancillary_info.ancillary_objects import Companies

from .manager import (
    debt_to_ratio,
    current_ratio,
    return_on_equity,
    equity_per_share,
    price_per_earnings,
    price_book_value
    )


class CalculatedStats:
    def __init__(self):
        session_factory()

    def populate_tables(self):
        # Get ancillary data
        df_companies = AncillaryInfo().get_companies_joined()
        df_params = AncillaryInfo().get_parameters_joined()

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
            df_share_price = share_price_instance.get_share_joined_filtered(company_tidm)

            # Get Financial Data
            financial_instance = Financial()
            df = financial_instance.get_financial_data_joined_filtered(company_tidm)
            df['param_name_report_section'] = df['param_name'] + '_' + df['report_section']
            df_pivot = df.pivot(
                columns="time_stamp", index="param_name_report_section", values="value"
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

            print('STOP')
