import pandas as pd


def debt_to_ratio(df_pivot):
    df_tl = _dataframe_slice(
        df_pivot, "Total liabilities_Liabilities"
    ).reset_index(drop=True)
    df_te = _dataframe_slice(df_pivot, "Total equity_Equity").reset_index(
        drop=True
    )
    df_d_e = df_tl.div(df_te)
    df_d_e.index = ["Debt to Equity (D/E)"]

    return df_d_e


def current_ratio(df_pivot):
    df_ca = _dataframe_slice(
        df_pivot, "Current assets_Assets"
    ).reset_index(drop=True)
    df_cl = _dataframe_slice(
        df_pivot, "Current liabilities_Liabilities"
    ).reset_index(drop=True)
    if not df_ca.empty and not df_cl.empty:
        df_cr = df_ca.div(df_cl)
        df_cr.index = ["Current Ratio"]

    return df_cr


def return_on_equity(df_pivot):
    df_profit = _dataframe_slice(
        df_pivot, "Profit for financial year_Continuous Operatings"
    ).reset_index(drop=True)
    df_nav = _dataframe_slice(
        df_pivot, "Shareholders funds (NAV)_Equity"
    ).reset_index(drop=True)
    if not df_profit.empty and not df_nav.empty:
        df_roe = df_profit.div(df_nav)
        df_roe.index = ["Return on Equity (ROE)"]

    return df_roe


def equity_per_share(df_pivot):
    df_nav = _dataframe_slice(
        df_pivot, "Shareholders funds (NAV)_Equity"
    ).reset_index(drop=True)
    df_shares = _dataframe_slice(
        df_pivot, "Average shares (diluted)_Other"
    ).reset_index(drop=True)
    if not df_nav.empty and not df_shares.empty:
        df_eps = df_nav.div(df_shares)
        df_eps.index = ["Equity (Book Value) Per Share"]

    return df_eps


def price_per_earnings(df_pivot):
    df_mark_cap = _dataframe_slice(
        df_pivot, "Market capitalisation_Other"
    ).reset_index(drop=True)
    df_profit = _dataframe_slice(
        df_pivot, "Profit for financial year_Continuous Operatings"
    ).reset_index(drop=True)
    if not df_mark_cap.empty and not df_profit.empty:
        df_ppe = df_mark_cap.div(df_profit)
        df_ppe.index = ["Price to Earnings (P/E)"]

    return df_ppe


def price_book_value(df_pivot, df_eps):
    df_mark_cap = _dataframe_slice(
        df_pivot, "Market capitalisation_Other"
    ).reset_index(drop=True)
    df_shares = _dataframe_slice(
        df_pivot, "Average shares (diluted)_Other"
    ).reset_index(drop=True)
    if not df_mark_cap.empty and not df_shares.empty:
        df_pbv = df_mark_cap.div(df_shares)
        df_pbv.index = ["Price to Book Value (Equity)"]

    df_equity = _dataframe_slice(
        df_pbv, "Price to Book Value (Equity)"
    ).reset_index(drop=True)
    df_eps = _dataframe_slice(
        df_eps, "Equity (Book Value) Per Share"
    ).reset_index(drop=True)
    if not df_equity.empty and not df_eps.empty:
        df_pbv = df_equity.div(df_eps)
        df_pbv.index = ["Price to Book Value (Equity)"]

    return df_pbv


def _dataframe_slice(df_input, row_title):
    try:
        result = df_input[row_title:row_title]
        return result
    except KeyError:
        return pd.DataFrame()
