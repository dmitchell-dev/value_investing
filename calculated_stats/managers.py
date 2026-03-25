"""
calculated_stats/managers.py
============================
Core financial calculation library for the Value Investing application.

All calculation functions accept pandas DataFrames produced by pivoting the
FinancialReports queryset (rows = parameter names, columns = report dates).
They return a single-row DataFrame with the same column structure so results
can be concatenated before being written to CalculatedStats.

Warren Buffett investment criteria covered:
  ✓ Return on Equity (ROE)          – target > 15% consistently
  ✓ Return on Capital Employed (ROCE) – target > 15%
  ✓ Return on Invested Capital (ROIC) – Buffett's preferred efficiency metric
  ✓ Debt-to-Equity ratio            – conservative measure using total liabilities
  ✓ Current Ratio                   – target > 1.5 for safety
  ✓ Debt Ratio                      – total debt / 5-yr avg earnings (< 5 years)
  ✓ Free Cash Flow                  – strong, consistent positive FCF
  ✓ Owner Earnings                  – Buffett's preferred FCF measure (1986 letter)
  ✓ Net Margin                      – target > 20% for competitive moat
  ✓ Gross Margin                    – consistently high = pricing power
  ✓ Operating Margin                – operating efficiency before financing costs
  ✓ Interest Coverage               – target > 5x; measures debt safety
  ✓ Dividend Cover                  – earnings / dividends paid
  ✓ Dividend Payout Ratio           – retained earnings are reinvestment capacity
  ✓ DCF Intrinsic Value             – two-stage discounted cash flow model
  ✓ Margin of Safety                – (IV – Price) / IV × 100; positive = undervalued
"""

from django.db.models import QuerySet
import pandas as pd
import numpy as np
from datetime import timedelta


# ---------------------------------------------------------------------------
# QuerySet helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Balance Sheet metrics
# ---------------------------------------------------------------------------

def total_equity(df_pivot):
    """
    Total Equity = Total Assets - Total Liabilities

    Buffett context: The book value of the firm owned by shareholders.
    Rising equity over time (without share issuance) signals retained earnings
    and value creation. Buffett looks for consistent equity growth.

    Falls back to reading "Total Equity" directly from the pivot when
    "Total Liabilities" is not present (e.g. seeded data).
    """
    # Prefer directly available "Total Equity" row (e.g. seeded from Balance Sheet)
    df_direct = _dataframe_slice(df_pivot, "Total Equity")
    if not df_direct.empty:
        df_t_e = df_direct.reset_index(drop=True)
        df_t_e.index = ["Total Equity"]
        return df_t_e

    # Fall back to calculation: Total Assets - Total Liabilities
    df_tl = _dataframe_slice(df_pivot, "Total Liabilities").reset_index(drop=True)
    df_ta = _dataframe_slice(df_pivot, "Total Assets").reset_index(drop=True)
    if df_tl.empty or df_ta.empty:
        return pd.DataFrame()
    df_t_e = df_ta - df_tl
    df_t_e.index = ["Total Equity"]
    return df_t_e


def capital_employed(df_pivot):
    """
    Capital Employed = Total Assets - Total Current Liabilities

    Represents the long-term capital base used to generate profits (equity plus
    long-term debt). Used as the denominator in ROCE. A growing capital base
    that is efficiently deployed signals quality management.
    """
    df_ta = _dataframe_slice(df_pivot, "Total Assets").reset_index(drop=True)
    df_tcl = _dataframe_slice(df_pivot, "Total Current Liabilities").reset_index(drop=True)
    if df_ta.empty or df_tcl.empty:
        return pd.DataFrame()
    df_c_e = df_ta - df_tcl
    df_c_e.index = ["Capital Employed"]
    return df_c_e


def current_ratio(df_pivot):
    """
    Current Ratio = Total Current Assets / Total Current Liabilities

    Liquidity measure. A ratio > 1.5 provides a comfortable cushion; < 1.0
    means current liabilities exceed current assets (potential cash crunch).
    Buffett prefers businesses that don't need large current asset buffers,
    but the ratio should comfortably cover short-term obligations.
    """
    df_ca = _dataframe_slice(df_pivot, "Total Current Assets").reset_index(drop=True)
    df_cl = _dataframe_slice(df_pivot, "Total Current Liabilities").reset_index(drop=True)
    if not df_ca.empty and not df_cl.empty:
        df_cr = df_ca.div(df_cl)
        df_cr.index = ["Current Ratio"]
    else:
        df_cr = df_ca  # returns empty DataFrame preserving column structure
    return df_cr


def debt_to_eq_ratio(df_pivot, df_t_e):
    """
    Debt to Equity (D/E) = Total Liabilities / Total Equity

    This uses Total Liabilities (conservative) rather than financial debt only,
    capturing all obligations. Buffett prefers companies with low D/E — ideally
    < 0.5 for non-financial companies — as high debt magnifies downside risk
    and constrains management's flexibility during downturns.
    """
    df_tl = _dataframe_slice(df_pivot, "Total Liabilities").reset_index(drop=True)
    if df_tl.empty or df_t_e.empty:
        return pd.DataFrame()
    df_d_e = df_tl.div(df_t_e.reset_index(drop=True))
    df_d_e.index = ["Debt to Equity"]
    return df_d_e


# ---------------------------------------------------------------------------
# Share price helpers
# ---------------------------------------------------------------------------

def share_price(df_pivot, df_share_price):
    """
    Share price matched to each financial report date.

    Searches for an exact date match first, then looks forward up to 14 days
    to find the nearest trading day. This gives the market price at the time
    each annual report was published, enabling historical valuation analysis
    (e.g. was the stock cheap when results were released?).
    """
    price_list = []
    date_list = []
    for date in list(df_pivot.columns):
        share_price_slice = df_share_price[df_share_price.time_stamp == date]
        if share_price_slice.empty:
            # No exact match — walk forward up to 14 days to find nearest trade
            for i in range(1, 15):
                date_shifted = date + timedelta(days=i)
                share_price_slice = df_share_price[
                    df_share_price.time_stamp == date_shifted
                ]
                if not share_price_slice.empty:
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
    Market Capitalisation = Shares Outstanding × Share Price

    The market's current valuation of the entire company. Used as the
    denominator in P/E, P/B, earnings yield, and annual yield calculations.
    """
    df_s_o = _dataframe_slice(df_pivot, "Shares Outstanding").reset_index(drop=True)
    if df_s_o.empty or df_share_price_reduced.empty:
        return pd.DataFrame()
    df_m_c = df_s_o.reset_index(drop=True) * df_share_price_reduced.reset_index(drop=True)
    df_m_c.index = ["Market Capitalisation"]
    return df_m_c


def enterprise_value(df_pivot, df_m_c):
    """
    Enterprise Value = Market Capitalisation + Total Liabilities - Cash & Equivalents

    EV represents the total acquisition cost of a business — what you would
    pay to buy the whole company including assumption of debt, less cash you
    would receive. Preferred over market cap alone for cross-company comparison
    because it neutralises differences in capital structure.
    """
    if df_m_c.empty:
        return pd.DataFrame()
    df_t_l = _dataframe_slice(df_pivot, "Total Liabilities").reset_index(drop=True)
    df_t_c_st = _dataframe_slice(df_pivot, "Total Cash and Short Term").reset_index(drop=True)
    df_e_v = df_m_c.reset_index(drop=True) + df_t_l - df_t_c_st
    df_e_v.index = ["Enterprise Value"]
    return df_e_v


# ---------------------------------------------------------------------------
# Cash flow metrics
# ---------------------------------------------------------------------------

def free_cash_flow(df_pivot):
    """
    Free Cash Flow (FCF) = Operating Cash Flow + Capital Expenditures

    NOTE: Capital Expenditures are stored as negative values in the database
    (cash outflow convention), so addition is used rather than subtraction.
    FCF = cash the business generates after maintaining/expanding its asset
    base. Buffett regards this as the true measure of earning power — a company
    that consistently produces strong FCF can self-fund growth, pay dividends,
    buy back shares, and weather recessions without needing external capital.
    """
    df_ocf = _dataframe_slice(df_pivot, "Operating Cash Flow").reset_index(drop=True)
    df_ce = _dataframe_slice(df_pivot, "Capital Expenditure").reset_index(drop=True)
    if df_ocf.empty:
        return pd.DataFrame()
    # CapEx stored negative; adding gives OCF - |CapEx|
    df_fcf = df_ocf + df_ce
    df_fcf.index = ["Free Cash Flow"]
    return df_fcf


def owner_earnings(df_pivot):
    """
    Owner Earnings = Net Income + Depreciation & Amortisation
                     - Capital Expenditures - Change in Working Capital

    Coined by Warren Buffett in his 1986 Berkshire Hathaway letter, Owner
    Earnings is his preferred measure of a company's true cash-generating
    ability. It adjusts reported net income for non-cash charges (D&A) and
    the actual reinvestment required to maintain competitive position (CapEx
    and working capital changes).

    Unlike reported EPS, Owner Earnings cannot be easily manipulated through
    accounting choices. Consistent growth in Owner Earnings per share is a
    hallmark of Buffett's ideal investment.

    NOTE: Change in Working Capital = prior year WC - current year WC.
          Positive change means WC increased (cash consumed); negative means
          WC decreased (cash released). Working Capital = Current Assets -
          Current Liabilities.
          CapEx is stored negative in DB so addition is correct.
    """
    df_ni = _dataframe_slice(df_pivot, "Net Income").reset_index(drop=True)
    df_da = _dataframe_slice(df_pivot, "Depreciation and Amortization").reset_index(drop=True)
    df_ce = _dataframe_slice(df_pivot, "Capital Expenditure").reset_index(drop=True)  # stored negative
    df_ca = _dataframe_slice(df_pivot, "Total Current Assets").reset_index(drop=True)
    df_cl = _dataframe_slice(df_pivot, "Total Current Liabilities").reset_index(drop=True)

    if df_ni.empty or df_da.empty or df_ce.empty:
        return pd.DataFrame()

    # Working capital change: positive means more WC tied up (cash out)
    if not df_ca.empty and not df_cl.empty:
        df_wc = df_ca - df_cl
        # Shift one period to get prior year WC; first period has no prior → 0
        df_wc_prior = df_wc.shift(1, axis=1).fillna(0)
        df_delta_wc = df_wc - df_wc_prior
    else:
        df_delta_wc = pd.DataFrame(0, index=df_ni.index, columns=df_ni.columns)

    # Owner Earnings: NI + D&A + CapEx(negative) - ΔWorkingCapital
    df_oe = df_ni + df_da + df_ce - df_delta_wc
    df_oe.index = ["Owner Earnings"]
    return df_oe


# ---------------------------------------------------------------------------
# Profitability / margin metrics
# ---------------------------------------------------------------------------

def net_margin(df_pivot):
    """
    Net Margin = Net Income / Total Revenue × 100  (expressed as %)

    The percentage of revenue that becomes profit after all costs, taxes and
    interest. Buffett looks for companies with consistently high and stable net
    margins (> 20%) as a signal of durable competitive advantage (moat).
    Declining net margins over time suggest increasing competition or cost
    pressures eroding the moat.
    """
    df_ni = _dataframe_slice(df_pivot, "Net Income").reset_index(drop=True)
    df_rev = _dataframe_slice(df_pivot, "Total Revenue").reset_index(drop=True)
    if df_ni.empty or df_rev.empty:
        return pd.DataFrame()
    df_nm = df_ni.div(df_rev) * 100
    df_nm.index = ["Net Margin"]
    return df_nm


def gross_margin(df_pivot):
    """
    Gross Margin = Gross Profit / Total Revenue × 100  (expressed as %)

    The percentage of revenue retained after direct production costs (COGS).
    Buffett views consistently high gross margins (> 40%) as one of the
    clearest indicators of a durable competitive moat — it means the company
    has pricing power and/or a structural cost advantage over competitors.
    Companies with gross margins that fluctuate widely or trend downward are
    typically operating in commodity-like industries with no pricing power.
    """
    df_gp = _dataframe_slice(df_pivot, "Gross Profit").reset_index(drop=True)
    df_rev = _dataframe_slice(df_pivot, "Total Revenue").reset_index(drop=True)
    if df_gp.empty or df_rev.empty:
        return pd.DataFrame()
    df_gm = df_gp.div(df_rev) * 100
    df_gm.index = ["Gross Margin"]
    return df_gm


def operating_margin(df_pivot):
    """
    Operating Margin = Operating Income / Total Revenue × 100  (expressed as %)

    The percentage of revenue remaining after operating costs but before
    interest and taxes. Operating Income (EBIT) removes the effect of capital
    structure, making it useful for comparing companies with different levels
    of debt. Buffett looks for stable or growing operating margins, which
    indicate management is controlling costs as the business scales.
    """
    df_oi = _dataframe_slice(df_pivot, "Operating Income").reset_index(drop=True)
    df_rev = _dataframe_slice(df_pivot, "Total Revenue").reset_index(drop=True)
    if df_oi.empty or df_rev.empty:
        return pd.DataFrame()
    df_om = df_oi.div(df_rev) * 100
    df_om.index = ["Operating Margin"]
    return df_om


# ---------------------------------------------------------------------------
# Return metrics
# ---------------------------------------------------------------------------

def return_on_equity(df_pivot, df_t_e):
    """
    Return on Equity (ROE) = Net Income / Total Equity × 100  (expressed as %)

    Measures how effectively management uses shareholder capital to generate
    profit. Buffett's minimum threshold is consistently > 15% ROE over a
    10-year period. A sustained high ROE without excessive debt indicates a
    genuine competitive advantage rather than financial engineering.

    Watch for artificially inflated ROE caused by share buybacks reducing
    equity, or high leverage increasing the denominator — always cross-check
    against D/E and absolute earnings growth.
    """
    df_ni = _dataframe_slice(df_pivot, "Net Income").reset_index(drop=True)
    if df_ni.empty or df_t_e.empty:
        return pd.DataFrame()
    df_roe = df_ni.div(df_t_e.reset_index(drop=True)) * 100
    df_roe.index = ["Return on Equity"]
    return df_roe


def roce(df_pivot, df_c_e):
    """
    Return on Capital Employed (ROCE) = Net Income / Capital Employed × 100  (%)

    Measures the return generated on all long-term capital (equity + long-term
    debt). More comprehensive than ROE as it includes debt-financed assets.
    Buffett looks for ROCE consistently above the company's cost of capital
    (typically > 15%). A declining ROCE over time suggests the business is
    reinvesting at lower returns, destroying value for shareholders.
    """
    df_n_i = _dataframe_slice(df_pivot, "Net Income").reset_index(drop=True)
    if df_n_i.empty or df_c_e.empty:
        return pd.DataFrame()
    df_roce = df_n_i.div(df_c_e.reset_index(drop=True)) * 100
    df_roce.index = ["ROCE"]
    return df_roce


def roic(df_pivot, df_t_e):
    """
    Return on Invested Capital (ROIC) = Net Income / Invested Capital × 100  (%)

    Invested Capital = Total Equity + Long-term Debt - Cash & Equivalents

    ROIC is arguably Buffett's most important efficiency metric. It measures
    how much profit the business generates for every pound/dollar of capital
    deployed by both equity holders and debt providers. The key insight is
    comparing ROIC to the Weighted Average Cost of Capital (WACC):
      - ROIC > WACC: business is creating value (earning more than it costs)
      - ROIC < WACC: business is destroying value even if reporting a profit

    Target: consistently > 15% is exceptional; > 10% is acceptable.
    The durability of high ROIC is the hallmark of a Buffett-style moat.

    NOTE: Long-term Debt is sourced from the "Long Term Debt" parameter.
          Cash & Equivalents from "Total Cash and Short Term".
    """
    df_ni = _dataframe_slice(df_pivot, "Net Income").reset_index(drop=True)
    df_ltd = _dataframe_slice(df_pivot, "Long Term Debt").reset_index(drop=True)
    df_cash = _dataframe_slice(df_pivot, "Total Cash and Short Term").reset_index(drop=True)

    if df_ni.empty or df_t_e.empty:
        return pd.DataFrame()

    # Invested Capital = Equity + LT Debt - Cash
    df_ic = df_t_e.reset_index(drop=True)
    if not df_ltd.empty:
        df_ic = df_ic + df_ltd
    if not df_cash.empty:
        df_ic = df_ic - df_cash

    # Guard against zero / negative invested capital (e.g. negative equity firms)
    df_ic = df_ic.replace(0, float("nan"))

    df_roic = df_ni.div(df_ic) * 100
    df_roic.index = ["Return on Invested Capital (ROIC)"]
    return df_roic


# ---------------------------------------------------------------------------
# Per-share metrics
# ---------------------------------------------------------------------------

def dividends_per_share(df_pivot):
    """
    Dividends Per Share = Dividend Payout / Shares Outstanding

    NOTE: Dividend Payout is stored as a negative value (cash outflow). The
    ×-1 corrects the sign to give a positive per-share figure.

    Buffett prefers businesses that either pay no dividend (reinvesting at high
    ROIC) or grow their dividend consistently over time. A rising DPS trend
    alongside rising EPS confirms sustainable dividend growth.
    """
    df_s_o = _dataframe_slice(df_pivot, "Shares Outstanding").reset_index(drop=True)
    df_dpo = _dataframe_slice(df_pivot, "Dividend Payout").reset_index(drop=True)
    if df_s_o.empty or df_dpo.empty:
        return pd.DataFrame()
    df_dps = df_dpo.div(df_s_o.reset_index(drop=True)) * -1
    df_dps.index = ["Dividends Per Share"]
    return df_dps


def equity_per_share(df_pivot, df_t_e):
    """
    Equity (Book Value) Per Share = Total Equity / Shares Outstanding

    The net asset value attributable to each share. Buffett tracked book value
    per share growth as a proxy for intrinsic value growth in early Berkshire
    letters. Consistent book value per share growth (without dilution) confirms
    the business is genuinely accumulating wealth for shareholders.
    """
    df_s_o = _dataframe_slice(df_pivot, "Shares Outstanding").reset_index(drop=True)
    if df_t_e.empty or df_s_o.empty:
        return pd.DataFrame()
    df_eps = df_t_e.reset_index(drop=True).div(df_s_o.reset_index(drop=True))
    df_eps.index = ["Equity (Book Value) Per Share"]
    return df_eps


def div_cover(df_pivot):
    """
    Dividend Cover = Net Income / Dividend Payout

    NOTE: Dividend Payout is stored as negative; ×-1 corrects the sign.

    Measures how many times over the company could pay its dividend from
    earnings. Cover > 2× is considered safe; < 1.5× raises sustainability
    concerns. A declining trend in dividend cover signals dividends may be
    cut if earnings deteriorate.
    """
    df_n_i = _dataframe_slice(df_pivot, "Net Income").reset_index(drop=True)
    df_dpo = _dataframe_slice(df_pivot, "Dividend Payout").reset_index(drop=True)
    if df_n_i.empty or df_dpo.empty:
        return pd.DataFrame()
    df_div_cover = df_n_i.div(df_dpo) * -1
    df_div_cover.index = ["Dividend Cover"]
    return df_div_cover


def dividend_payout_ratio(df_pivot):
    """
    Dividend Payout Ratio = Dividend Payout / Net Income × 100  (expressed as %)

    NOTE: Dividend Payout stored as negative; ×-1 gives a positive ratio.

    The percentage of earnings distributed as dividends. The complement
    (100% - payout ratio) is the retention ratio — capital retained for
    reinvestment. Buffett prefers companies with low payout ratios that
    reinvest retained earnings at high ROIC, compounding value internally.
    A payout ratio > 80% leaves little room to fund growth or weather downturns.
    A payout ratio of 0% (no dividend) is fine if ROIC is high.
    """
    df_ni = _dataframe_slice(df_pivot, "Net Income").reset_index(drop=True)
    df_dpo = _dataframe_slice(df_pivot, "Dividend Payout").reset_index(drop=True)
    if df_ni.empty or df_dpo.empty:
        return pd.DataFrame()
    # Guard zero net income (loss years would invert the ratio)
    df_ni_safe = df_ni.replace(0, float("nan"))
    df_dpr = (df_dpo.div(df_ni_safe) * -1) * 100
    df_dpr.index = ["Dividend Payout Ratio"]
    return df_dpr


# ---------------------------------------------------------------------------
# Valuation metrics
# ---------------------------------------------------------------------------

def price_per_earnings(df_pivot, df_m_c):
    """
    Price to Earnings (P/E) = Market Capitalisation / Net Income

    The classic valuation multiple. Equivalent to Share Price / EPS.
    Buffett pays close attention to the earnings yield (1/P/E) relative to
    long-term bond yields — he will invest in equities when the earnings yield
    offers an adequate premium over risk-free rates. He generally avoids
    companies trading at very high P/E ratios as the future growth required
    to justify the price leaves no margin of safety.
    """
    df_n_i = _dataframe_slice(df_pivot, "Net Income").reset_index(drop=True)
    if df_m_c.empty or df_n_i.empty:
        return pd.DataFrame()
    df_ppe = df_m_c.reset_index(drop=True).div(df_n_i)
    df_ppe.index = ["Price to Earnings"]
    return df_ppe


def price_book_value(df_pivot, df_m_c, df_eps):
    """
    Price to Book Value (P/B) = Share Price / Equity (Book Value) Per Share
                               = (Market Cap / Shares) / Equity Per Share

    Compares the market price to the balance sheet value of equity. P/B < 1
    can signal undervaluation (buying $1 of assets for less than $1), though
    it can also indicate distress. Buffett used P/B extensively in early
    Buffett Partnership days; he now focuses more on earnings power.
    Still useful as a cross-check against DCF intrinsic value.
    """
    df_s_o = _dataframe_slice(df_pivot, "Shares Outstanding").reset_index(drop=True)
    df_m_c = df_m_c.reset_index(drop=True)
    df_eps = df_eps.reset_index(drop=True)
    if df_m_c.empty or df_s_o.empty or df_eps.empty:
        return pd.DataFrame()
    df_interim = df_m_c.div(df_s_o)
    df_pbv = df_interim.div(df_eps)
    df_pbv.index = ["Price to Book Value (Equity)"]
    return df_pbv


def earnings_yield(df_pivot, df_m_c):
    """
    Earnings Yield = Net Income / Market Capitalisation × 100  (expressed as %)

    The inverse of the P/E ratio, expressed as a percentage. Answers the
    question: "For every £100 of market cap, how many pounds of earnings
    does the company generate?" Directly comparable to bond yields and
    savings rates. Buffett has stated he looks to invest in equities when
    their earnings yield offers a meaningful premium over US Treasury yields.

    Example: P/E = 10 → Earnings Yield = 10%
             P/E = 25 → Earnings Yield = 4% (less attractive vs bonds)

    NOTE: This uses Market Capitalisation (not Enterprise Value) to keep
    the numerator (post-interest Net Income) and denominator (equity value)
    on a consistent post-debt basis. See ROIC for an EV-based comparison.
    """
    df_n_i = _dataframe_slice(df_pivot, "Net Income").reset_index(drop=True)
    if df_n_i.empty or df_m_c.empty:
        return pd.DataFrame()
    df_e_yield = df_n_i.div(df_m_c.reset_index(drop=True)) * 100
    df_e_yield.index = ["Earnings Yield"]
    return df_e_yield


def annual_yield(df_pivot, df_m_c):
    """
    Annual Dividend Yield = Dividend Payout / Market Capitalisation × 100  (%)

    NOTE: Dividend Payout stored as negative; ×-1 gives positive yield.

    The income return from dividends relative to the market price paid.
    Buffett does not prioritise dividend yield — he prefers management to
    retain and reinvest earnings at high ROIC. However, dividend yield is
    relevant when assessing total return and comparing income alternatives.
    A high yield relative to history can be a contrarian buying signal,
    but should be cross-checked against dividend cover to ensure sustainability.
    """
    df_dpo = _dataframe_slice(df_pivot, "Dividend Payout").reset_index(drop=True)
    if df_dpo.empty or df_m_c.empty:
        return pd.DataFrame()
    df_a_yield = (df_dpo.div(df_m_c.reset_index(drop=True)) * -1) * 100
    df_a_yield.index = ["Annual Yield (Return)"]
    return df_a_yield


def interest_coverage(df_pivot):
    """
    Interest Coverage Ratio = Operating Income / Interest Expense

    Measures how many times a company can cover its interest payments from
    operating profit (EBIT). A higher ratio signals greater financial safety.

    Buffett's thresholds:
      > 5×  — comfortable; company can service debt even in a downturn
      2–5×  — manageable but leaves limited buffer
      < 2×  — dangerous; a modest drop in earnings could trigger default

    Operating Income is used as the EBIT proxy (earnings before interest and
    tax, before financing decisions affect the result).

    NOTE: Interest Expense is stored as a negative value (cash outflow);
    ×-1 normalises it to a positive denominator.
    """
    df_oi = _dataframe_slice(df_pivot, "Operating Income").reset_index(drop=True)
    df_ie = _dataframe_slice(df_pivot, "Interest Expense").reset_index(drop=True)
    if df_oi.empty or df_ie.empty:
        return pd.DataFrame()
    # Interest Expense is stored negative; negate to get positive denominator
    df_ie_pos = df_ie * -1
    # Guard zero interest expense (debt-free companies → infinite coverage)
    df_ie_safe = df_ie_pos.replace(0, float("nan"))
    df_ic = df_oi.div(df_ie_safe)
    df_ic.index = ["Interest Coverage"]
    return df_ic


# ---------------------------------------------------------------------------
# DCF valuation
# ---------------------------------------------------------------------------

def dcf_intrinsic_value(df_pivot, df_dcf_variables, df_fcf):
    """
    DCF Intrinsic Value per Share — Two-Stage Discounted Cash Flow Model

    Stage 1 — Explicit forecast (Years 1–10):
    Each year's FCF is grown at the short-term growth rate and discounted
    back to present value at the discount rate:

        PV_1..10 = Σ [FCF₀ × (1 + g)ⁿ / (1 + r)ⁿ]  for n = 1..10

    Stage 2 — Terminal value (Year 10 onwards):
    At the end of Year 10 a Gordon Growth Model perpetuity is applied using
    the long-term growth rate. The terminal value is calculated at the end
    of Year 10 and discounted back 10 periods to present value:

        FCF₁₁   = FCF₀ × (1 + g)¹⁰ × (1 + ltg)
        TV       = FCF₁₁ / (r − ltg)
        PV_TV    = TV / (1 + r)¹⁰

    Intrinsic Value per Share = (PV_1..10 + PV_TV) / Shares Outstanding

    Input parameters (from DcfVariables model per company):
      est_growth_rate  — short-term FCF CAGR for years 1–10 (e.g. 0.08 = 8%)
      est_disc_rate    — discount rate / required rate of return (e.g. 0.10)
      est_ltg_rate     — perpetual long-term growth rate beyond year 10 (e.g. 0.03)
                         MUST be < est_disc_rate or the terminal value is infinite

    Buffett context: Buffett describes intrinsic value as "the discounted value
    of the cash that can be taken out of a business during its remaining life."
    He uses an owner-earnings based FCF and typically requires a significant
    margin of safety between intrinsic value and market price before investing.
    """
    df_s_o = _dataframe_slice(df_pivot, "Shares Outstanding").reset_index(drop=True)

    if df_fcf.empty or df_s_o.empty or df_dcf_variables.empty:
        return pd.DataFrame()

    intrinsic_value_list = []
    base_year_fcf = df_fcf.reset_index(drop=True)
    shares_outstanding = df_s_o.reset_index(drop=True)

    g = df_dcf_variables.est_growth_rate[0]    # short-term growth rate
    ltg = df_dcf_variables.est_ltg_rate[0]     # long-term (terminal) growth rate
    r = df_dcf_variables.est_disc_rate[0]      # discount rate

    # Validate: ltg must be strictly less than r to avoid infinite terminal value
    if ltg >= r:
        raise ValueError(
            f"Long-term growth rate ({ltg}) must be less than discount rate ({r}). "
            "Increase the discount rate or reduce the long-term growth rate."
        )

    ten_year_list = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    for col in range(0, df_pivot.shape[1]):
        fcf0 = base_year_fcf.values[0][col]           # base year FCF
        shares = shares_outstanding.values[0][col]     # shares outstanding

        # Stage 1: PV of years 1–10 explicit FCF forecasts
        pv_stage1 = np.sum(
            (fcf0 * np.power(1 + g, ten_year_list))
            / np.power(1 + r, ten_year_list)
        )

        # Stage 2: Terminal value at end of Year 10 (Gordon Growth Model)
        # FCF in Year 11 = FCF₀ × (1+g)¹⁰ × (1+ltg)
        # TV at Year 10  = FCF₁₁ / (r − ltg)
        # PV of TV        = TV / (1+r)¹⁰
        fcf_year11 = fcf0 * pow(1 + g, 10) * (1 + ltg)
        tv = fcf_year11 / (r - ltg)
        pv_tv = tv / pow(1 + r, 10)

        intrinsic_value_share = (pv_stage1 + pv_tv) / shares
        intrinsic_value_list.append(intrinsic_value_share)

    # Build output DataFrame
    df_iv = pd.DataFrame(intrinsic_value_list).transpose()
    df_iv.columns = list(df_pivot.columns)
    df_iv.index = ["DCF Intrinsic Value"]

    # Record the input assumptions alongside the result for auditability
    def _const_row(value, label):
        df = pd.DataFrame([value] * df_pivot.shape[1]).transpose()
        df.columns = list(df_pivot.columns)
        df.index = [label]
        return df

    df_dcf_intrinsic_value = pd.concat([
        _const_row(g,   "Estimated Growth Rate"),
        _const_row(ltg, "Estimated Long Term Growth Rate"),
        _const_row(r,   "Estimated Discount Rate"),
        df_iv,
    ])
    return df_dcf_intrinsic_value


def margin_of_safety(df_share_price_reduced, df_dcf_intrinsic_value):
    """
    Margin of Safety = (Intrinsic Value − Share Price) / Intrinsic Value × 100  (%)

    The central concept of value investing, popularised by Benjamin Graham and
    adopted by Buffett. A positive MOS means the stock is trading at a discount
    to intrinsic value — the investor is buying a £1 of value for less than £1.
    A negative MOS means the stock is overvalued relative to its DCF value.

    Buffett typically requires a MOS of at least 25–30% before buying, to
    protect against errors in the intrinsic value estimate, unexpected
    deterioration in business performance, or adverse macro events.

    Examples:
      IV = £200, Price = £150  → MOS = (200−150)/200 × 100 = +25%  (buy)
      IV = £200, Price = £200  → MOS = 0%                           (fair value)
      IV = £200, Price = £250  → MOS = (200−250)/200 × 100 = −25%  (overvalued)
    """
    df_iv = _dataframe_slice(df_dcf_intrinsic_value, "DCF Intrinsic Value").reset_index(drop=True)
    if df_iv.empty or df_share_price_reduced.empty:
        return pd.DataFrame()
    df_price = df_share_price_reduced.reset_index(drop=True)

    # Guard zero intrinsic value
    df_iv_safe = df_iv.replace(0, float("nan"))

    df_mos = ((df_iv_safe - df_price) / df_iv_safe) * 100
    df_mos.index = ["Margin of Safety"]
    return df_mos


def latest_margin_of_safety(df_dcf_intrinsic_value, df_share_price_reduced, df_share_price):
    """
    Latest Margin of Safety = (Intrinsic Value − Latest Price) / Intrinsic Value × 100  (%)

    Identical in formula to Margin of Safety but uses the most recent available
    share price rather than the historical price matched to each report date.
    This gives a real-time picture of current undervaluation/overvaluation
    relative to the DCF intrinsic value calculated from the latest accounts.

    The latest price replaces the last column of the historical price series so
    the row structure remains consistent with other calculated stats.
    """
    df_iv = _dataframe_slice(df_dcf_intrinsic_value, "DCF Intrinsic Value").reset_index(drop=True)
    if df_iv.empty or df_share_price_reduced.empty or df_share_price.empty:
        return pd.DataFrame()

    # Replace the final column with the most recent share price
    latest_price = df_share_price.iloc[-1:]["value_adjusted"].values[0]
    df_latest_price_row = df_share_price_reduced.copy()
    df_latest_price_row.iloc[:, -1] = latest_price

    df_iv_safe = df_iv.replace(0, float("nan"))
    df_latest_mos = ((df_iv_safe - df_latest_price_row.reset_index(drop=True)) / df_iv_safe) * 100
    df_latest_mos.index = ["Latest Margin of Safety"]
    return df_latest_mos


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _dataframe_slice(df_input, row_title):
    """
    Safely extract a single named row from a pivoted DataFrame.
    Returns an empty DataFrame (rather than raising KeyError or TypeError)
    when the row is not present or the index is not string-based.
    """
    if df_input.empty:
        return pd.DataFrame()
    try:
        return df_input[row_title:row_title]
    except (KeyError, TypeError):
        return pd.DataFrame()
