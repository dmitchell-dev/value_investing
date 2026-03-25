import pandas as pd
import numpy as np
from datetime import timedelta
import math
import statistics


def debt_to_ratio(df_pivot):
    df_tl = _dataframe_slice(df_pivot, "Total liabilities_Liabilities").reset_index(
        drop=True
    )
    df_te = _dataframe_slice(df_pivot, "Total equity_Equity").reset_index(drop=True)
    df_d_e = df_tl.div(df_te)
    df_d_e.index = ["Debt to Equity (D/E)"]

    return df_d_e


def current_ratio(df_pivot):
    df_ca = _dataframe_slice(df_pivot, "Current assets_Assets").reset_index(drop=True)
    df_cl = _dataframe_slice(df_pivot, "Current liabilities_Liabilities").reset_index(
        drop=True
    )
    if not df_ca.empty and not df_cl.empty:
        df_cr = df_ca.div(df_cl)
        df_cr.index = ["Current Ratio"]
    else:
        # empty dataframe with correct dates
        df_cr = df_ca
    return df_cr


def return_on_equity(df_pivot):
    df_profit = _dataframe_slice(
        df_pivot, "Profit for financial year_Continuous Operatings"
    ).reset_index(drop=True)
    df_nav = _dataframe_slice(df_pivot, "Shareholders funds (NAV)_Equity").reset_index(
        drop=True
    )
    if not df_profit.empty and not df_nav.empty:
        df_roe = df_profit.div(df_nav) * 100  # Express as percentage
        df_roe.index = ["Return on Equity (ROE)"]

    return df_roe


def equity_per_share(df_pivot):
    df_nav = _dataframe_slice(df_pivot, "Shareholders funds (NAV)_Equity").reset_index(
        drop=True
    )
    df_shares = _dataframe_slice(
        df_pivot, "Average shares (diluted)_Other"
    ).reset_index(drop=True)
    if not df_nav.empty and not df_shares.empty:
        df_eps = df_nav.div(df_shares)
        df_eps.index = ["Equity (Book Value) Per Share"]

    return df_eps


def price_per_earnings(df_pivot):
    df_mark_cap = _dataframe_slice(df_pivot, "Market capitalisation_Other").reset_index(
        drop=True
    )
    df_profit = _dataframe_slice(
        df_pivot, "Profit for financial year_Continuous Operatings"
    ).reset_index(drop=True)
    if not df_mark_cap.empty and not df_profit.empty:
        df_ppe = df_mark_cap.div(df_profit)
        df_ppe.index = ["Price to Earnings (P/E)"]

    return df_ppe


def price_book_value(df_pivot, df_eps):
    df_mark_cap = _dataframe_slice(df_pivot, "Market capitalisation_Other").reset_index(
        drop=True
    )
    df_shares = _dataframe_slice(
        df_pivot, "Average shares (diluted)_Other"
    ).reset_index(drop=True)
    if not df_mark_cap.empty and not df_shares.empty:
        df_pbv = df_mark_cap.div(df_shares)
        df_pbv.index = ["Price to Book Value (Equity)"]

    df_equity = _dataframe_slice(df_pbv, "Price to Book Value (Equity)").reset_index(
        drop=True
    )
    df_eps = _dataframe_slice(df_eps, "Equity (Book Value) Per Share").reset_index(
        drop=True
    )
    if not df_equity.empty and not df_eps.empty:
        df_pbv = df_equity.div(df_eps)
        df_pbv.index = ["Price to Book Value (Equity)"]

    return df_pbv


def annual_yield(df_pivot):
    df_profit = _dataframe_slice(
        df_pivot, "Profit for financial year_Continuous Operatings"
    ).reset_index(drop=True)
    df_mark_cap = _dataframe_slice(df_pivot, "Market capitalisation_Other").reset_index(
        drop=True
    )
    if not df_profit.empty and not df_mark_cap.empty:
        df_a_return = df_profit.div(df_mark_cap)
        df_a_return.index = ["Annual Yield (Return)"]

    return df_a_return


def fcf_growth_rate(df_pivot):
    df_fcf = _dataframe_slice(
        df_pivot, "Free cash flow (FCF)_Free Cash Flow"
    ).reset_index(drop=True)
    fcf_gr_list = df_fcf.values.tolist()[0]

    growth_rate = []
    for gr in range(1, len(fcf_gr_list)):
        if fcf_gr_list[gr - 1] != 0:
            gnumbers = (
                (fcf_gr_list[gr] - fcf_gr_list[gr - 1]) / fcf_gr_list[gr - 1] * 100
            )
        else:
            gnumbers = None
        growth_rate.append(gnumbers)
    growth_rate.insert(0, None)
    df_fcf_gr = pd.DataFrame(growth_rate).transpose()
    df_fcf_gr.columns = list(df_fcf.columns)
    df_fcf_gr.index = ["Free cash flow (FCF)"]

    return (df_fcf_gr, df_fcf)


def div_payment(df_pivot):
    df_div_payment = np.where(
        (_dataframe_slice(df_pivot, "Dividend (adjusted) ps_Per Share Values") > 0),
        "yes",
        "no",
    )
    df_div_payment = pd.DataFrame(df_div_payment, columns=df_pivot.columns)
    df_div_payment.index = ["Dividend Payment"]

    return df_div_payment


def dcf_intrinsic_value(df_pivot, df_dcf_variables):
    intrinsic_value_list = []
    base_year_fcf = _dataframe_slice(df_pivot, "Free cash flow (FCF)_Free Cash Flow")
    shares_outstanding = _dataframe_slice(df_pivot, "Average shares (diluted)_Other")
    growth_rate = df_dcf_variables[
        df_dcf_variables.param_name == ("Estimated Growth Rate")
    ]
    longterm_growth_rate = df_dcf_variables[
        df_dcf_variables.param_name == ("Estimated Long Term Growth Rate")
    ]
    discount_rate = df_dcf_variables[
        df_dcf_variables.param_name == "Estimated Discount Rate"
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


def share_price(df_fcf, df_share_price):
    price_list = []
    date_list = []
    for date in list(df_fcf.columns):
        share_price_slice = df_share_price[df_share_price.time_stamp == date]
        if share_price_slice.empty:
            # If there is not an exact date for the share price
            # from the report date, then increase 3 days until
            # the clostest share price is found
            for i in range(1, 4):
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


def revenue_growth(df_pivot):
    revenue_growth_list = []
    year_count = 0
    row_title = "Turnover_Continuous Operatings"
    # TODO add in banks and insurance companies
    if not _dataframe_slice(df_pivot, row_title).empty:
        df_turnover = _dataframe_slice(df_pivot, row_title)
        for col in range(0, df_pivot.shape[1]):
            year_count = year_count + 1

            if year_count == 1:
                revenue_growth_list.append(None)
            else:
                current_year_turnover = df_turnover.values[0][col]
                previous_year_turnover = df_turnover.values[0][col - 1]

                if current_year_turnover > previous_year_turnover:
                    revenue_growth_list.append("yes")
                else:
                    revenue_growth_list.append("no")
    else:
        revenue_growth_list = [None] * df_pivot.shape[1]

    df_revenue_growth = pd.DataFrame(data=revenue_growth_list).transpose()
    df_revenue_growth.columns = list(df_pivot.columns)
    if not df_revenue_growth.empty:
        df_revenue_growth.index = ["Revenue Growth"]

    return df_revenue_growth


def eps_growth(df_pivot):
    eps_growth_list = []
    year_count = 0
    row_title = "EPS norm. continuous_Per Share Values"

    df_eps = _dataframe_slice(df_pivot, row_title)
    for col in range(0, df_pivot.shape[1]):
        year_count = year_count + 1

        if year_count == 1:
            eps_growth_list.append(None)
        else:
            current_year_eps = df_eps.values[0][col]
            previous_year_eps = df_eps.values[0][col - 1]

            if current_year_eps > previous_year_eps:
                eps_growth_list.append("yes")
            else:
                eps_growth_list.append("no")

    df_eps_growth = pd.DataFrame(data=eps_growth_list).transpose()
    df_eps_growth.columns = list(df_pivot.columns)
    if not df_eps_growth.empty:
        df_eps_growth.index = ["EPS Growth"]

    return df_eps_growth


def dividend_growth(df_pivot):
    div_growth_list = []
    year_count = 0
    row_title = "Dividend (adjusted) ps_Per Share Values"

    df_div = _dataframe_slice(df_pivot, row_title)
    for col in range(0, df_pivot.shape[1]):
        year_count = year_count + 1

        if year_count == 1:
            div_growth_list.append(None)
        else:
            current_year_div = df_div.values[0][col]
            if math.isnan(current_year_div):
                current_year_div = 0
            previous_year_div = df_div.values[0][col - 1]
            if math.isnan(previous_year_div):
                previous_year_div = 0

            if current_year_div > previous_year_div:
                div_growth_list.append("yes")
            else:
                div_growth_list.append("no")

    df_div_growth = pd.DataFrame(data=div_growth_list).transpose()
    df_div_growth.columns = list(df_pivot.columns)
    if not df_div_growth.empty:
        df_div_growth.index = ["Dividend Growth"]

    return df_div_growth


def growth_quality(df_pivot, df_revenue_growth, df_eps_growth, df_div_growth):
    growth_qual_list = []
    year_count = 0
    df_growth_all = pd.concat([df_revenue_growth, df_eps_growth, df_div_growth])
    growth_count = df_growth_all[df_growth_all == "yes"].count()

    for col in range(0, df_pivot.shape[1]):
        df_growth_all[df_growth_all == "yes"].count()[year_count]

        if year_count < 9:
            growth_qual_list.append(None)
        elif year_count >= 9:
            growth_qual_list.append(
                growth_count[year_count - 9 : year_count + 1].sum() / 30 * 100
            )

        year_count = year_count + 1

    df_growth_quality = pd.DataFrame(data=growth_qual_list).transpose()
    df_growth_quality.columns = list(df_pivot.columns)
    if not df_growth_quality.empty:
        df_growth_quality.index = ["Growth Quality"]

    return df_growth_quality


def revenue_growth_10_year(df_pivot):
    turnover_list = []
    rev_growth_list = []
    year_count = 0
    row_title = "Turnover_Continuous Operatings"

    # TODO add in banks and insurance companies
    if not _dataframe_slice(df_pivot, row_title).empty:
        df_turnover = _dataframe_slice(df_pivot, row_title)
        for col in range(0, df_pivot.shape[1]):
            year_count = year_count + 1

            # Build first 10 years list
            current_year_turnover = df_turnover.values[0][col]
            turnover_list.append(current_year_turnover)

            # Start calculation after 10 years
            if year_count < 10:
                rev_growth_list.append(None)
            elif year_count >= 10:
                first_three_years = sum(turnover_list[:3])
                last_three_years = sum(turnover_list[7:])
                rev_growth_year = ((last_three_years / first_three_years) - 1) * 100
                rev_growth_list.append(rev_growth_year)

                # Remove first
                turnover_list.pop(0)
    else:
        rev_growth_list = [None] * df_pivot.shape[1]

    df_rev_growth_10 = pd.DataFrame(data=rev_growth_list).transpose()
    df_rev_growth_10.columns = list(df_pivot.columns)
    if not df_rev_growth_10.empty:
        df_rev_growth_10.index = ["Revenue Growth (10 year)"]

    return df_rev_growth_10


def earnings_growth_10_year(df_pivot):
    eps_list = []
    eps_growth_list = []
    year_count = 0
    row_title = "EPS norm. continuous_Per Share Values"

    df_eps = _dataframe_slice(df_pivot, row_title)
    for col in range(0, df_pivot.shape[1]):
        year_count = year_count + 1

        # Build first 10 years list
        current_year_eps = df_eps.values[0][col]
        eps_list.append(current_year_eps)

        # Start calculation after 10 years
        if year_count < 10:
            eps_growth_list.append(None)
        elif year_count >= 10:
            first_three_years = sum(eps_list[:3])
            last_three_years = sum(eps_list[7:])
            if first_three_years != 0:
                eps_growth_year = ((last_three_years / first_three_years) - 1) * 100
            else:
                eps_growth_year = 0
            eps_growth_list.append(eps_growth_year)

            # Remove first
            eps_list.pop(0)

    df_eps_growth_10 = pd.DataFrame(data=eps_growth_list).transpose()
    df_eps_growth_10.columns = list(df_pivot.columns)
    if not df_eps_growth_10.empty:
        df_eps_growth_10.index = ["Earnings Growth (10 year)"]

    return df_eps_growth_10


def dividend_growth_10_year(df_pivot):
    div_list = []
    div_growth_list = []
    year_count = 0
    row_title = "Dividend (adjusted) ps_Per Share Values"

    df_div = _dataframe_slice(df_pivot, row_title)
    for col in range(0, df_pivot.shape[1]):
        year_count = year_count + 1

        # Build first 10 years list
        current_year_div = df_div.values[0][col]
        if math.isnan(current_year_div):
            current_year_div = 0
        div_list.append(current_year_div)

        # Start calculation after 10 years
        if year_count < 10:
            div_growth_list.append(None)
        elif year_count >= 10:
            first_three_years = sum(div_list[:3])
            last_three_years = sum(div_list[7:])
            if first_three_years == 0:
                div_growth_year = 0
            else:
                div_growth_year = ((last_three_years / first_three_years) - 1) * 100
            div_growth_list.append(div_growth_year)

            # Remove first
            div_list.pop(0)

    df_div_growth_10 = pd.DataFrame(data=div_growth_list).transpose()
    df_div_growth_10.columns = list(df_pivot.columns)
    if not df_div_growth_10.empty:
        df_div_growth_10.index = ["Dividend Growth (10 year)"]

    return df_div_growth_10


def overall_growth_and_rate(
    df_pivot, df_rev_growth_10, df_eps_growth_10, df_div_growth_10
):
    df_growth_rates = pd.concat([df_rev_growth_10, df_eps_growth_10, df_div_growth_10])

    df_overall_growth = pd.DataFrame(df_growth_rates.mean(axis=0)).transpose()
    df_overall_growth.columns = list(df_pivot.columns)
    if not df_overall_growth.empty:
        df_overall_growth.index = ["Overall Growth (10 year)"]

    # Replace any values over -100 with -100
    # as this would produce imaginary numbers (NaN)
    df_overall_growth[df_overall_growth < -100] = -100

    # Calculate Rate
    df_growth_rate = (pow((1 + (df_overall_growth / 100)), (1 / 7)) - 1) * 100
    df_growth_rate.index = ["Growth Rate (10 year)"]

    return (df_overall_growth, df_growth_rate)


def capital_employed(df_pivot):
    ce_list = []
    year_count = 0

    row_title = "Total assets_Assets"
    df_assets = _dataframe_slice(df_pivot, row_title)
    row_title = "Current liabilities_Liabilities"

    # TODO add in banks and insurance companies
    if not _dataframe_slice(df_pivot, row_title).empty:
        df_liabilities = _dataframe_slice(df_pivot, row_title)

        for col in range(0, df_pivot.shape[1]):
            year_count = year_count + 1

            # Build first 10 years list
            current_year_assets = df_assets.values[0][col]
            if math.isnan(current_year_assets):
                current_year_assets = 0
            current_year_liabilities = df_liabilities.values[0][col]
            if math.isnan(current_year_liabilities):
                current_year_liabilities = 0

            ce_list.append(current_year_assets - current_year_liabilities)
    else:
        ce_list = [None] * df_pivot.shape[1]

    df_ce = pd.DataFrame(data=ce_list).transpose()
    df_ce.columns = list(df_pivot.columns)
    if not df_ce.empty:
        df_ce.index = ["Capital Employed"]

    return df_ce


def roce(df_pivot, df_ce):
    row_title = "Profit for financial year_Continuous Operatings"
    if not _dataframe_slice(df_pivot, row_title).empty:
        df_profit = _dataframe_slice(df_pivot, row_title).reset_index(drop=True)
        df_roce = df_profit.div(df_ce.reset_index(drop=True)) * 100
    else:
        roce_list = [None] * df_pivot.shape[1]
        df_roce = pd.DataFrame(data=roce_list).transpose()
        df_roce.columns = list(df_pivot.columns)

    if not df_roce.empty:
        df_roce.index = ["ROCE"]

    return df_roce


def median_roce_10_year(df_pivot, df_roce):
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
                        current_year_share_price / statistics.mean(eps_list)
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
                            current_year_share_price / statistics.mean(div_list)
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


def net_margin(df_pivot):
    """
    Net Profit Margin = (Net Income / Total Revenue) × 100

    Warren Buffett context
    ----------------------
    Buffett looks for companies with *consistently* high net margins — ideally
    above 20% — as a hallmark of durable competitive advantage (moat). A
    business that can reliably convert a large fraction of revenue into profit
    is rarely reliant on a single product cycle or heavily exposed to commodity
    pricing.

    Trend matters more than a single year: a margin that is stable or slowly
    widening over a decade signals pricing power; a declining margin suggests
    competitive pressure or cost inflation the company cannot pass on.

    Data: Profit for financial year / Turnover, both from the Continuous
    Operatings section. Returns percentage values (e.g. 22.5 = 22.5%).
    """
    df_profit = _dataframe_slice(
        df_pivot, "Profit for financial year_Continuous Operatings"
    ).reset_index(drop=True)
    df_turnover = _dataframe_slice(
        df_pivot, "Turnover_Continuous Operatings"
    ).reset_index(drop=True)

    if not df_profit.empty and not df_turnover.empty:
        df_nm = df_profit.div(df_turnover) * 100
        df_nm.index = ["Net Margin"]
    else:
        nm_list = [None] * df_pivot.shape[1]
        df_nm = pd.DataFrame(data=nm_list).transpose()
        df_nm.columns = list(df_pivot.columns)
        df_nm.index = ["Net Margin"]

    return df_nm


def gross_margin(df_pivot):
    """
    Gross Profit Margin = (Gross Profit / Total Revenue) × 100

    Warren Buffett context
    ----------------------
    Gross margin is the first and most durable indicator of competitive moat.
    Companies Buffett favours — Coca-Cola, See's Candies, American Express —
    all exhibit gross margins that are structurally higher than their industry
    peers and are *stable over time*.

    A gross margin consistently above 40% often indicates:
      • Brand strength that supports premium pricing
      • Low cost of goods sold relative to selling price
      • Limited direct commodity exposure

    Banks and insurance companies do not report a traditional gross profit line;
    this function guards against an empty slice and returns None for those firms.

    Data: Gross profit / Turnover, both from Continuous Operatings section.
    Returns percentage values (e.g. 45.0 = 45%).
    """
    df_gross = _dataframe_slice(
        df_pivot, "Gross profit_Continuous Operatings"
    ).reset_index(drop=True)
    df_turnover = _dataframe_slice(
        df_pivot, "Turnover_Continuous Operatings"
    ).reset_index(drop=True)

    if not df_gross.empty and not df_turnover.empty:
        df_gm = df_gross.div(df_turnover) * 100
        df_gm.index = ["Gross Margin"]
    else:
        gm_list = [None] * df_pivot.shape[1]
        df_gm = pd.DataFrame(data=gm_list).transpose()
        df_gm.columns = list(df_pivot.columns)
        df_gm.index = ["Gross Margin"]

    return df_gm


def operating_margin(df_pivot):
    """
    Operating Profit Margin = (Operating Profit / Total Revenue) × 100

    Warren Buffett context
    ----------------------
    Operating margin captures the profitability of the core business *before*
    interest and tax, stripping out capital-structure effects. It answers the
    question: how efficiently does management convert revenue into operating
    profit from the actual business activity?

    Buffett historically seeks operating margins above 15%. The gap between
    gross margin and operating margin reveals the SG&A burden — a wide gap can
    indicate excessive overhead or heavy reinvestment; a narrow gap suggests a
    lean, scalable business model.

    Data: Operating profit / Turnover. Returns percentage values.
    """
    df_op_profit = _dataframe_slice(
        df_pivot, "Operating profit_Continuous Operatings"
    ).reset_index(drop=True)
    df_turnover = _dataframe_slice(
        df_pivot, "Turnover_Continuous Operatings"
    ).reset_index(drop=True)

    if not df_op_profit.empty and not df_turnover.empty:
        df_om = df_op_profit.div(df_turnover) * 100
        df_om.index = ["Operating Margin"]
    else:
        om_list = [None] * df_pivot.shape[1]
        df_om = pd.DataFrame(data=om_list).transpose()
        df_om.columns = list(df_pivot.columns)
        df_om.index = ["Operating Margin"]

    return df_om


def interest_coverage(df_pivot):
    """
    Interest Coverage Ratio = Operating Profit / Finance Costs (Interest Expense)

    Warren Buffett context
    ----------------------
    Buffett is deeply averse to financial fragility. A company that must
    dedicate a significant portion of its operating profit to service debt has
    reduced financial flexibility and is vulnerable in an economic downturn.

    Rule of thumb:
      • > 5×   — strong; debt is not a constraint
      • 3–5×   — adequate; manageable but warrants monitoring
      • < 3×   — concerning; debt service consumes too much operating profit
      • < 1×   — critical; the company cannot cover its interest from operations

    Note: Finance costs are typically a negative number in UK accounts. This
    function takes the absolute value of finance costs as the denominator.
    Returns the coverage multiple (e.g. 8.2 means interest is covered 8.2×).
    """
    df_op_profit = _dataframe_slice(
        df_pivot, "Operating profit_Continuous Operatings"
    ).reset_index(drop=True)
    df_finance_costs = _dataframe_slice(
        df_pivot, "Finance costs_Continuous Operatings"
    ).reset_index(drop=True)

    if not df_op_profit.empty and not df_finance_costs.empty:
        # Finance costs are typically reported as a negative; take absolute value
        df_ic = df_op_profit.div(df_finance_costs.abs())
        df_ic.index = ["Interest Coverage"]
    else:
        ic_list = [None] * df_pivot.shape[1]
        df_ic = pd.DataFrame(data=ic_list).transpose()
        df_ic.columns = list(df_pivot.columns)
        df_ic.index = ["Interest Coverage"]

    return df_ic


def dividend_payout_ratio(df_pivot):
    """
    Dividend Payout Ratio = (Dividends Paid / Net Income) × 100

    Warren Buffett context
    ----------------------
    Buffett actually *prefers* companies that retain most of their earnings
    rather than paying them out — provided management can reinvest those
    retained earnings at high rates of return (i.e. high ROCE / ROE). When
    Berkshire Hathaway acquired See's Candies, it never paid a dividend;
    instead, profits were redeployed into better opportunities.

    However, a dividend payout ratio is still a useful quality indicator:
      • Very high (> 80%) — may signal limited reinvestment opportunities or
        that the dividend is being maintained at the expense of future growth.
      • Moderate (30–60%) — balanced; management is both rewarding shareholders
        and reinvesting for growth.
      • Very low (< 20%) — aggressive reinvestment; only attractive if ROCE is
        demonstrably high.

    Data: Dividends paid is negative in cash flow statements; this function
    multiplies by −1 before dividing by net income so the ratio is positive.
    Returns percentage values (e.g. 45.0 = 45% of earnings paid as dividends).
    """
    df_dividends = _dataframe_slice(
        df_pivot, "Dividends paid_Cash Flow"
    ).reset_index(drop=True)
    df_profit = _dataframe_slice(
        df_pivot, "Profit for financial year_Continuous Operatings"
    ).reset_index(drop=True)

    if not df_dividends.empty and not df_profit.empty:
        # Dividends paid is negative in cash flow — multiply by -1 for positive ratio
        df_dpr = (df_dividends * -1).div(df_profit) * 100
        df_dpr.index = ["Dividend Payout Ratio"]
    else:
        dpr_list = [None] * df_pivot.shape[1]
        df_dpr = pd.DataFrame(data=dpr_list).transpose()
        df_dpr.columns = list(df_pivot.columns)
        df_dpr.index = ["Dividend Payout Ratio"]

    return df_dpr


def _dataframe_slice(df_input, row_title):
    try:
        result = df_input[row_title:row_title]
        return result
    except KeyError:
        return pd.DataFrame()
