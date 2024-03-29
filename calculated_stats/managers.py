from django.db.models import QuerySet
import pandas as pd
import numpy as np
from datetime import timedelta


class CalculatedStatsQueryset(QuerySet):
    def get_table_joined_filtered(self, tidm):
        return self.values(
            "id",
            "time_stamp",
            "value",
            "company__tidm",
            "parameter__param_name",
        ).filter(company__tidm=tidm)

    def get_table_filtered(self, tidm):
        return self.values(
            "id",
            "time_stamp",
            "value",
            "company",
            "parameter",
        ).filter(company__tidm=tidm)

    def get_table_joined(self):
        return self.values(
            "id",
            "time_stamp",
            "value",
            "company__tidm",
            "parameter__param_name",
        )

    def get_latest_date(self, tidm):
        if self.filter(company__tidm=tidm):
            return self.filter(company__tidm=tidm).latest("time_stamp")
        else:
            return []


def total_equity(df_pivot):
    """
    Total Equity =
    Balance Sheet Total Assets
    - Total Liabilities
    """

    df_tl = _dataframe_slice(df_pivot, "Total Liabilities").reset_index(drop=True)
    df_ta = _dataframe_slice(df_pivot, "Total Assets").reset_index(drop=True)
    df_t_e = df_ta - df_tl
    df_t_e.index = ["Total Equity"]

    return df_t_e


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
                    price_list.append(share_price_slice.iloc[0]["value_adjusted"])
                    date_list.append(date)
                    break
        else:
            price_list.append(share_price_slice.iloc[0]["value_adjusted"])
            date_list.append(share_price_slice.iloc[0]["time_stamp"])

    df_share_price_reduced = pd.DataFrame(data=price_list).transpose()
    df_share_price_reduced.columns = date_list
    if not df_share_price_reduced.empty:
        df_share_price_reduced.index = ["Share Price"]

    return df_share_price_reduced


def market_cap(df_pivot, df_share_price_reduced):
    """
    Market Capitalisation =
    Shares Outstanding
    * Share Price
    """
    df_s_o = _dataframe_slice(df_pivot, "Shares Outstanding").reset_index(drop=True)
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

    df_t_l = _dataframe_slice(df_pivot, "Total Liabilities").reset_index(drop=True)
    df_t_c_st = _dataframe_slice(df_pivot, "Total Cash and Short Term").reset_index(
        drop=True
    )

    df_e_v = df_m_c.reset_index(drop=True) + df_t_l - df_t_c_st
    df_e_v.index = ["Enterprise Value"]

    return df_e_v


def free_cash_flow(df_pivot):
    """
    Free Cash Flow =
    Operating Cash Flow -
    Capital Expenditures
    """

    df_ocf = _dataframe_slice(df_pivot, "Operating Cash Flow").reset_index(drop=True)
    df_ce = _dataframe_slice(df_pivot, "Capital Expenditures").reset_index(drop=True)

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

    df_ta = _dataframe_slice(df_pivot, "Total Assets").reset_index(drop=True)
    df_tcl = _dataframe_slice(df_pivot, "Total Current Liabilities").reset_index(
        drop=True
    )

    df_c_e = df_ta - df_tcl
    df_c_e.index = ["Capital Employed"]

    return df_c_e


def dividends_per_share(df_pivot):
    """
    Dividends Per Share =
    Dividend Payout /
    Shares Outstanding
    """

    df_s_o = _dataframe_slice(df_pivot, "Shares Outstanding").reset_index(drop=True)
    df_dpo = _dataframe_slice(df_pivot, "Dividend Payout").reset_index(drop=True)

    df_dps = df_dpo.div(df_s_o.reset_index(drop=True)) * -1
    df_dps.index = ["Dividends Per Share"]

    return df_dps


def debt_to_eq_ratio(df_pivot, df_t_e):
    """
    Debt to Equity (D/E) =
    Balance Sheet Total Liabilities
    / Total Equity
    """

    df_tl = _dataframe_slice(df_pivot, "Total Liabilities").reset_index(drop=True)
    df_d_e = df_tl.div(df_t_e.reset_index(drop=True))
    df_d_e.index = ["Debt to Equity (D/E)"]

    return df_d_e


def current_ratio(df_pivot):
    """
    Current Ratio =
    Total Current Assets
    / Total Current Liabilities
    """

    df_ca = _dataframe_slice(df_pivot, "Total Current Assets").reset_index(drop=True)
    df_cl = _dataframe_slice(df_pivot, "Total Current Liabilities").reset_index(
        drop=True
    )
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

    df_ni = _dataframe_slice(df_pivot, "Net Income").reset_index(drop=True)
    if not df_ni.empty:
        df_roe = df_ni.div(df_t_e.reset_index(drop=True)) * 100
        df_roe.index = ["Return on Equity (ROE)"]

    return df_roe


def equity_per_share(df_pivot, df_t_e):
    """
    Equity (Book Value) Per Share =
    Total Equity
    / Shares Outstanding
    """

    df_s_o = _dataframe_slice(df_pivot, "Shares Outstanding").reset_index(drop=True)
    if not df_t_e.empty and not df_s_o.empty:
        df_eps = df_t_e.reset_index(drop=True).div(df_s_o.reset_index(drop=True))
        df_eps.index = ["Equity (Book Value) Per Share"]

    return df_eps


def price_per_earnings(df_pivot, df_m_c):
    """
    Price to Earnings (P/E) =
    Market Capitalisation
    / Net Income
    """

    df_n_i = _dataframe_slice(df_pivot, "Net Income").reset_index(drop=True)
    if not df_m_c.empty and not df_n_i.empty:
        df_ppe = df_m_c.reset_index(drop=True).div(df_n_i)
        df_ppe.index = ["Price to Earnings (P/E)"]

    return df_ppe


def price_book_value(df_pivot, df_m_c, df_eps):
    """
    Price to Book Value (Equity) =
    (Market Capitalisation / Shares Outstanding)
    / Equity (Book Value) Per Share
    """

    df_s_o = _dataframe_slice(df_pivot, "Shares Outstanding").reset_index(drop=True)

    df_m_c = df_m_c.reset_index(drop=True)
    df_eps = df_eps.reset_index(drop=True)

    if not df_eps.empty:
        df_interim = df_m_c.div(df_s_o)
        df_pbv = df_interim.div(df_eps)
        df_pbv.index = ["Price to Book Value (Equity)"]

    return df_pbv


def earnings_yield(df_pivot, df_e_v):
    """
    Earnings Yield =
    Net Income
    / Enterprise Value
    """

    df_n_i = _dataframe_slice(df_pivot, "Net Income").reset_index(drop=True)

    if not df_n_i.empty and not df_e_v.empty:
        df_e_yield = df_n_i.div(df_e_v.reset_index(drop=True)) * 100
        df_e_yield.index = ["Earnings Yield"]

    return df_e_yield


def annual_yield(df_pivot, df_m_c):
    """
    Annual Yield (Return) =
    Net Income
    / Market Capitalisation
    """

    df_n_i = _dataframe_slice(df_pivot, "Net Income").reset_index(drop=True)

    if not df_n_i.empty and not df_m_c.empty:
        df_a_yield = df_n_i.div(df_m_c.reset_index(drop=True)) * 100
        df_a_yield.index = ["Annual Yield (Return)"]

    return df_a_yield


def div_cover(df_pivot):
    """
    Dividend Cover =
    Net Income /
    Dividend Payout
    """

    df_n_i = _dataframe_slice(df_pivot, "Net Income").reset_index(drop=True)
    df_dpo = _dataframe_slice(df_pivot, "Dividend Payout").reset_index(drop=True)

    df_div_cover = df_n_i.div(df_dpo) * -1

    df_div_cover.index = ["Dividend Cover"]

    return df_div_cover


def dcf_intrinsic_value(df_pivot, df_dcf_variables, df_fcf):
    """
    Function(Free Cash Flow, Shares Outstanding)
    """

    df_s_o = _dataframe_slice(df_pivot, "Shares Outstanding").reset_index(drop=True)

    intrinsic_value_list = []
    base_year_fcf = df_fcf.reset_index(drop=True)
    shares_outstanding = df_s_o.reset_index(drop=True)

    growth_rate_value = df_dcf_variables.est_growth_rate[0]
    longterm_growth_rate_value = df_dcf_variables.est_ltg_rate[0]
    discount_rate_value = df_dcf_variables.est_disc_rate[0]

    for col in range(0, df_pivot.shape[1]):
        # Company report values
        base_year_fcf_value = base_year_fcf.values[0][col]
        shares_outstanding_value = shares_outstanding.values[0][col]

        # Input Variables
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
    df_dcf_intrinsic_value.index = ["Intrinsic Value"]

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
    Return on Capital Employed (ROCE) =
    Net Income /
    Capital Employed
    """

    df_n_i = _dataframe_slice(df_pivot, "Net Income").reset_index(drop=True)

    df_roce = df_n_i.div(df_c_e.reset_index(drop=True)) * 100

    df_roce.index = ["Return on Capital Employed (ROCE)"]

    return df_roce


def margin_of_safety(df_share_price_reduced, df_dcf_intrinsic_value):
    """
    Margin of Safety =
    Share Price / Intrinsic Value
    """

    df_dcf_intrinsic_value = _dataframe_slice(
        df_dcf_intrinsic_value, "Intrinsic Value"
    ).reset_index(drop=True)

    df_margin_of_safety = df_share_price_reduced.reset_index(drop=True).div(
        df_dcf_intrinsic_value
    )

    df_margin_of_safety.index = ["Margin of Safety"]

    return df_margin_of_safety


def latest_margin_of_safety(
    df_dcf_intrinsic_value, df_share_price_reduced, df_share_price
):
    """
    Latest Margin of Safety =
    Latest Share Price / Intrinsic Value
    """

    df_dcf_intrinsic_value = _dataframe_slice(
        df_dcf_intrinsic_value, "Intrinsic Value"
    ).reset_index(drop=True)
    # latest_intrinsic_value = df_dcf_intrinsic_value.iloc[:, -1][0]

    df_latest_share_price = df_share_price.iloc[-1:]
    latest_share_price = df_latest_share_price["value_adjusted"]

    # TODO populate row with latest share price
    df_latest_share_price_reduced = df_share_price_reduced.copy()
    df_latest_share_price_reduced.iloc[-1:] = latest_share_price

    df_latest_margin_of_safety = df_latest_share_price_reduced.reset_index(drop=True).div(
        df_dcf_intrinsic_value
    )

    df_latest_margin_of_safety.index = ["Latest Margin of Safety"]

    return df_latest_margin_of_safety


def _dataframe_slice(df_input, row_title):
    try:
        result = df_input[row_title:row_title]
        return result
    except KeyError:
        return pd.DataFrame()
