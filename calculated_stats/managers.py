from django.db.models import QuerySet
import pandas as pd
import numpy as np
from datetime import timedelta
import math
import statistics


class CalculatedStatsQueryset(QuerySet):
    def get_table_joined_filtered(self, tidm):
        return self.values(
            "time_stamp",
            "value",
            "company__tidm",
            "parameter__param_name",
        ).filter(company__tidm=tidm)

    def get_table_joined(self):
        return self.values(
            "time_stamp",
            "value",
            "company__tidm",
            "parameter__param_name",
        )


def total_equity(df_pivot):
    """
    Total Equity =
    Balance Sheet Total Assets
    - Total Liabilities
    """

    df_tl = _dataframe_slice(
        df_pivot, "Total Liabilities"
        ).reset_index(drop=True)
    df_ta = _dataframe_slice(
        df_pivot, "Total Assets"
        ).reset_index(drop=True)
    df_t_e = df_ta - df_tl
    df_t_e.index = ["Total Equity"]

    return df_t_e


def shares_outstanding(df_pivot):
    """
    Shares Outstanding =
    Net Income
    / Reported EPS
    """

    df_ni = _dataframe_slice(
        df_pivot, "Net Income"
        ).reset_index(drop=True)
    df_r_eps = _dataframe_slice(
        df_pivot, "Reported EPS"
        ).reset_index(drop=True)
    df_s_o = df_ni.div(df_r_eps)
    df_s_o.index = ["Shares Outstanding"]

    return df_s_o


def share_price(df_pivot, df_share_price):
    """
    Nearest share price to fundamental dates
    """

    price_list = []
    date_list = []
    for date in list(df_pivot.columns):
        share_price_slice = df_share_price[df_share_price.time_stamp == date]
        if share_price_slice.empty:
            # If there is not an exact date for the share price
            # from the report date, then increase 14 days until
            # the clostest share price is found
            for i in range(1, 15):
                date_shifted = date + timedelta(days=i)
                share_price_slice = df_share_price[
                    df_share_price.time_stamp == date_shifted
                ]
                if share_price_slice.empty:
                    pass
                else:
                    price_list.append(share_price_slice.values[0][2] / 100)
                    date_list.append(date)
                    break
        else:
            price_list.append(share_price_slice.values[0][2] / 100)
            date_list.append(share_price_slice.values[0][1])

    df_share_price_reduced = pd.DataFrame(data=price_list).transpose()
    df_share_price_reduced.columns = date_list
    if not df_share_price_reduced.empty:
        df_share_price_reduced.index = ["Share Price"]

    return df_share_price_reduced


def market_cap(df_s_o, df_share_price_reduced):
    """
    Market Capitalisation =
    Shares Outstanding
    * Share Price
    """

    df_m_c = df_s_o.reset_index(drop=True) * (
        df_share_price_reduced.reset_index(drop=True)
        )
    df_m_c.index = ["Market Capitalisation"]

    return df_m_c


def enterprise_value(df_pivot, df_m_c):
    """
    Enterprise Value =
    Market Capitalisation +
    Total Liabilities -
    Total Cash and Short Term
    """

    df_t_l = _dataframe_slice(
        df_pivot, "Total Liabilities"
        ).reset_index(drop=True)
    df_t_c_st = _dataframe_slice(
        df_pivot, "Total Cash and Short Term"
        ).reset_index(drop=True)

    df_e_v = df_m_c.reset_index(drop=True) + df_t_l - df_t_c_st
    df_e_v.index = ["Enterprise Value"]

    return df_e_v


def free_cash_flow(df_pivot):
    """
    Free Cash Flow =
    Operating Cash Flow -
    Capital Expenditures
    """

    df_ocf = _dataframe_slice(
        df_pivot, "Operating Cash Flow"
        ).reset_index(drop=True)
    df_ce = _dataframe_slice(
        df_pivot, "Capital Expenditures"
        ).reset_index(drop=True)

    # CE Negative in DB
    df_fcf = df_ocf + df_ce
    df_fcf.index = ["Free Cash Flow"]

    return df_fcf


def capital_employed(df_pivot):
    """
    Capital Employed =
    Total Assets -
    Total Current Liabilities
    """

    df_ta = _dataframe_slice(
        df_pivot, "Total Assets"
        ).reset_index(drop=True)
    df_tcl = _dataframe_slice(
        df_pivot, "Total Current Liabilities"
        ).reset_index(drop=True)

    df_c_e = df_ta - df_tcl
    df_c_e.index = ["Free Cash Flow"]

    return df_c_e


def dividends_per_share(df_pivot, df_s_o):
    """
    Dividends Per Share =
    Dividend Payout /
    Shares Outstanding
    """

    df_dpo = _dataframe_slice(
        df_pivot, "Dividend Payout"
        ).reset_index(drop=True)

    # CE Negative in DB
    df_dps = df_dpo.div(df_s_o.reset_index(drop=True))
    df_dps.index = ["Dividends Per Share"]

    return df_dps


def debt_to_eq_ratio(df_pivot, df_t_e):
    """
    Debt to Equity (D/E) =
    Balance Sheet Total Liabilities
    / Total Equity
    """

    df_tl = _dataframe_slice(
        df_pivot, "Total Liabilities"
        ).reset_index(drop=True)
    df_d_e = df_tl.div(df_t_e.reset_index(drop=True))
    df_d_e.index = ["Debt to Equity (D/E)"]

    return df_d_e


def current_ratio(df_pivot):
    """
    Current Ratio =
    Total Current Assets
    / Total Current Liabilities
    """

    df_ca = _dataframe_slice(
        df_pivot, "Total Current Assets"
        ).reset_index(drop=True)
    df_cl = _dataframe_slice(
        df_pivot, "Total Current Liabilities"
        ).reset_index(drop=True)
    if not df_ca.empty and not df_cl.empty:
        df_cr = df_ca.div(df_cl)
        df_cr.index = ["Current Ratio"]
    else:
        # empty dataframe with correct dates
        df_cr = df_ca
    return df_cr


def return_on_equity(df_pivot, df_t_e):
    """
    Return on Equity (ROE) =
    Net Income
    / Total Equity
    """

    df_ni = _dataframe_slice(
        df_pivot, "Net Income"
    ).reset_index(drop=True)
    if not df_ni.empty:
        df_roe = df_ni.div(df_t_e.reset_index(drop=True)) * 100
        df_roe.index = ["Return on Equity (ROE)"]

    return df_roe


def equity_per_share(df_t_e, df_s_o):
    """
    Equity (Book Value) Per Share =
    Total Equity
    / Shares Outstanding
    """

    if not df_t_e.empty and not df_s_o.empty:
        df_eps = df_t_e.reset_index(drop=True).div(
            df_s_o.reset_index(drop=True)
            )
        df_eps.index = ["Equity (Book Value) Per Share"]

    return df_eps


def price_per_earnings(df_pivot, df_m_c):
    """
    Price to Earnings (P/E) =
    Market Capitalisation
    / Net Income
    """

    df_n_i = _dataframe_slice(
        df_pivot, "Net Income"
        ).reset_index(drop=True)
    if not df_m_c.empty and not df_n_i.empty:
        df_ppe = df_m_c.reset_index(drop=True).div(df_n_i)
        df_ppe.index = ["Price to Earnings (P/E)"]

    return df_ppe


def price_book_value(df_m_c, df_s_o, df_eps):
    """
    Price to Book Value (Equity) =
    (Market Capitalisation / Shares Outstanding)
    / Equity (Book Value) Per Share
    """

    df_m_c = df_m_c.reset_index(drop=True)
    df_s_o = df_s_o.reset_index(drop=True)
    df_eps = df_eps.reset_index(drop=True)

    if not df_eps.empty:
        df_interim = df_m_c.div(df_s_o)
        df_pbv = df_interim.div(df_eps)
        df_pbv.index = ["Price to Book Value (Equity)"]

    return df_pbv


def annual_yield(df_pivot, df_e_v):
    """
    Earnings Yield (Return) =
    Net Income
    / Enterprise Value
    """

    df_n_i = _dataframe_slice(
        df_pivot, "Net Income"
    ).reset_index(drop=True)

    if not df_n_i.empty and not df_e_v.empty:
        df_a_return = df_n_i.div(df_e_v.reset_index(drop=True)) * 100
        df_a_return.index = ["Earnings Yield (Return)"]

    return df_a_return


def div_payment(df_dps):
    """
    Dividend Payment =
    if there has been dividend payment
    """

    for col_name in df_dps.columns:
        print(df_dps[col_name].iloc[0])
        print(type(df_dps[col_name].iloc[0]))

    df_div_payment = np.where(
        (np.isnan(df_dps)),
        "no",
        "yes",
    )
    df_div_payment = pd.DataFrame(df_div_payment, columns=df_dps.columns)
    df_div_payment.index = ["Dividend Payment"]

    return df_div_payment


def div_cover(df_pivot):
    """
    Dividend Cover =
    Net Income /
    Dividend Payout
    """

    df_n_i = _dataframe_slice(
        df_pivot, "Net Income"
    ).reset_index(drop=True)
    df_dpo = _dataframe_slice(
        df_pivot, "Dividend Payout"
    ).reset_index(drop=True)

    df_div_cover = df_n_i.div(df_dpo)

    df_div_cover.index = ["Dividend Cover"]

    return df_div_cover


def dcf_intrinsic_value(df_pivot, df_dcf_variables):
    """
    Function(dividends_per_share, shares_outstanding)
    TODO REALLY, should be FCF??
    """

    intrinsic_value_list = []
    base_year_fcf = _dataframe_slice(df_pivot, "Free cash flow (FCF)_Free Cash Flow")
    shares_outstanding = _dataframe_slice(df_pivot, "Average shares (diluted)_Other")
    growth_rate = df_dcf_variables[
        df_dcf_variables.parameter__param_name == ("Estimated Growth Rate")
    ]
    longterm_growth_rate = df_dcf_variables[
        df_dcf_variables.parameter__param_name == ("Estimated Long Term Growth Rate")
    ]
    discount_rate = df_dcf_variables[
        df_dcf_variables.parameter__param_name == "Estimated Discount Rate"
    ]

    for col in range(0, df_pivot.shape[1]):
        # Company report values
        base_year_fcf_value = base_year_fcf.values[0][col]
        shares_outstanding_value = shares_outstanding.values[0][col]

        # Input Variables
        growth_rate_value = growth_rate.values[0][1]
        longterm_growth_rate_value = longterm_growth_rate.values[0][1]
        discount_rate_value = discount_rate.values[0][1]
        ten_year_list = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        # Caclulation
        fcf = np.sum(
            (base_year_fcf_value * pow((1 + growth_rate_value), ten_year_list))
            / pow((1 + discount_rate_value), ten_year_list)
        )
        dpcf = (
            (
                base_year_fcf_value
                * pow((1 + growth_rate_value), 11)
                * (1 + longterm_growth_rate_value)
            )
            / (discount_rate_value - longterm_growth_rate_value)
        ) * (1 / pow((1 + discount_rate_value), 11))
        intrinsic_value_share = (fcf + dpcf) / shares_outstanding_value
        intrinsic_value_list.append(intrinsic_value_share)

    # Create Dataframe
    df_dcf_intrinsic_value = pd.DataFrame(intrinsic_value_list).transpose()
    df_dcf_intrinsic_value.columns = list(df_pivot.columns)
    df_dcf_intrinsic_value.index = ["DCF Intrinsic Value"]

    # Record input variables used in cals
    # Estimated Growth Rate
    df_est_growth_rate = pd.DataFrame(
        [growth_rate_value] * df_pivot.shape[1]
    ).transpose()
    df_est_growth_rate.columns = list(df_pivot.columns)
    df_est_growth_rate.index = ["Estimated Growth Rate"]

    # Estimated Long Term Growth Rate
    df_est_long_growth_rate = pd.DataFrame(
        [longterm_growth_rate_value] * df_pivot.shape[1]
    ).transpose()
    df_est_long_growth_rate.columns = list(df_pivot.columns)
    df_est_long_growth_rate.index = ["Estimated Long Term Growth Rate"]

    # Estimated Discount Rate
    df_est_discount_rate = pd.DataFrame(
        [discount_rate_value] * df_pivot.shape[1]
    ).transpose()
    df_est_discount_rate.columns = list(df_pivot.columns)
    df_est_discount_rate.index = ["Estimated Discount Rate"]

    df_dcf_intrinsic_value = pd.concat(
        [
            df_est_growth_rate,
            df_est_long_growth_rate,
            df_est_discount_rate,
            df_dcf_intrinsic_value,
        ]
    )

    return df_dcf_intrinsic_value


def roce(df_pivot, df_c_e):
    """
    TODO Notes Here
    """

    row_title = "Profit for financial year_Continuous Operatings"
    if not _dataframe_slice(df_pivot, row_title).empty:
        df_profit = _dataframe_slice(df_pivot, row_title).reset_index(drop=True)
        df_roce = df_profit.div(df_c_e.reset_index(drop=True)) * 100
    else:
        roce_list = [None] * df_pivot.shape[1]
        df_roce = pd.DataFrame(data=roce_list).transpose()
        df_roce.columns = list(df_pivot.columns)

    if not df_roce.empty:
        df_roce.index = ["ROCE"]

    return df_roce


def median_roce_10_year(df_pivot, df_roce):
    """
    TODO Notes Here
    """

    roce_list = []
    roce_growth_list = []
    year_count = 0

    for col in range(0, df_pivot.shape[1]):
        year_count = year_count + 1

        # Build first 10 years list
        current_year_roce = df_roce.values[0][col]
        if math.isnan(current_year_roce):
            current_year_roce = 0
        roce_list.append(current_year_roce)

        # Start calculation after 10 years
        if year_count < 10:
            roce_growth_list.append(None)
        elif year_count >= 10:
            roce_growth_list.append(statistics.median(roce_list))

            # Remove first
            roce_list.pop(0)

    df_roce_median = pd.DataFrame(data=roce_growth_list).transpose()
    df_roce_median.columns = list(df_pivot.columns)
    if not df_roce_median.empty:
        df_roce_median.index = ["Median ROCE (10 year)"]

    return df_roce_median


def debt_ratio(df_pivot):
    """
    TODO Notes Here
    """

    profit_list = []
    debt_ratio_list = []
    year_count = 0
    row_title = "Short term borrowing_Liabilities"
    if not _dataframe_slice(df_pivot, row_title).empty:
        df_short_borrowing = _dataframe_slice(df_pivot, row_title)

        row_title = "Profit for financial year_Continuous Operatings"
        df_profit = _dataframe_slice(df_pivot, row_title)
        row_title = "Short term borrowing_Liabilities"
        df_short_borrowing = (
            _dataframe_slice(df_pivot, row_title).reset_index(drop=True).fillna(0)
        )
        row_title = "Long term borrowing_Liabilities"
        df_long_borrowing = (
            _dataframe_slice(df_pivot, row_title).reset_index(drop=True).fillna(0)
        )
        df_borrowing = df_short_borrowing.add(df_long_borrowing)

        for col in range(0, df_pivot.shape[1]):
            year_count = year_count + 1

            # Build first 5 years list
            current_year_profit = df_profit.values[0][col]
            if math.isnan(current_year_profit):
                current_year_profit = 0
            profit_list.append(current_year_profit)
            current_year_borrowing = df_borrowing.values[0][col]
            if math.isnan(current_year_borrowing):
                current_year_borrowing = 0

            # Start calculation after 5 years
            if year_count < 5:
                debt_ratio_list.append(None)
            elif year_count >= 5:
                if statistics.mean(profit_list) != 0:
                    yearly_debt_ratio = current_year_borrowing / statistics.mean(
                        profit_list
                    )
                else:
                    yearly_debt_ratio = 0
                debt_ratio_list.append(yearly_debt_ratio)

                # Remove first
                profit_list.pop(0)
    else:
        debt_ratio_list = [None] * df_pivot.shape[1]

    df_debt_ratio = pd.DataFrame(data=debt_ratio_list).transpose()
    df_debt_ratio.columns = list(df_pivot.columns)
    if not df_debt_ratio.empty:
        df_debt_ratio.index = ["Debt Ratio"]

    return df_debt_ratio


def pe_10_year(df_pivot, df_calculated):
    """
    TODO Notes Here
    """

    eps_list = []
    ep10_list = []
    year_count = 0
    row_title = "EPS norm. continuous_Per Share Values"
    if not _dataframe_slice(df_pivot, row_title).empty:
        df_eps = _dataframe_slice(df_pivot, row_title)

        row_title = "Share Price"
        if not _dataframe_slice(df_calculated, row_title).empty:
            df_share_price = _dataframe_slice(df_calculated, row_title)

            for col in range(0, df_pivot.shape[1]):
                year_count = year_count + 1

                # Build first 10 years list
                current_year_eps = df_eps.values[0][col]
                if math.isnan(current_year_eps):
                    current_year_eps = 0
                eps_list.append(current_year_eps)

                # Start calculation after 10 years
                if year_count < 10:
                    ep10_list.append(None)
                elif year_count >= 10:
                    current_year_share_price = df_share_price.values[0][col]
                    if math.isnan(current_year_share_price):
                        current_year_share_price = 0
                    ep10_list.append(
                        (current_year_share_price / statistics.mean(eps_list)) * 100
                    )

                    # Remove first
                    eps_list.pop(0)
        else:
            ep10_list = [None] * df_pivot.shape[1]

    df_pe10 = pd.DataFrame(data=ep10_list).transpose()
    df_pe10.columns = list(df_pivot.columns)
    if not df_pe10.empty:
        df_pe10.index = ["PE10"]

    return df_pe10


def dp_10_year(df_pivot, df_calculated):
    """
    TODO Notes Here
    """

    div_list = []
    dp10_list = []
    year_count = 0
    row_title = "Dividend (adjusted) ps_Per Share Values"
    if not _dataframe_slice(df_pivot, row_title).empty:
        df_div = _dataframe_slice(df_pivot, row_title)

        row_title = "Share Price"
        if not _dataframe_slice(df_calculated, row_title).empty:
            df_share_price = _dataframe_slice(df_calculated, row_title)

            for col in range(0, df_pivot.shape[1]):
                year_count = year_count + 1

                # Build first 10 years list
                current_year_div = df_div.values[0][col]
                if math.isnan(current_year_div):
                    current_year_div = 0
                div_list.append(current_year_div)

                # Start calculation after 10 years
                if year_count < 10:
                    dp10_list.append(None)
                elif year_count >= 10:
                    current_year_share_price = df_share_price.values[0][col]
                    if math.isnan(current_year_share_price):
                        current_year_share_price = 0
                    if statistics.mean(div_list) != 0:
                        dp10_list.append(
                            (current_year_share_price / statistics.mean(div_list)) * 100
                        )
                    else:
                        dp10_list.append(0)

                    # Remove first
                    div_list.pop(0)
        else:
            dp10_list = [None] * df_pivot.shape[1]

    df_dp10 = pd.DataFrame(data=dp10_list).transpose()
    df_dp10.columns = list(df_pivot.columns)
    if not df_dp10.empty:
        df_dp10.index = ["DP10"]

    return df_dp10


def _dataframe_slice(df_input, row_title):
    try:
        result = df_input[row_title:row_title]
        return result
    except KeyError:
        return pd.DataFrame()
