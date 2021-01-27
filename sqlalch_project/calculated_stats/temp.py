# Annual Yield (Return) =
# Profit for financial year_Continuous Operatings
# / Market capitalisation_Other
df_profit = self._dataframe_slice(
    df_pivot, "Profit for financial year_Continuous Operatings"
).reset_index(drop=True)
df_mark_cap = self._dataframe_slice(
    df_pivot, "Market capitalisation_Other"
).reset_index(drop=True)
if not df_profit.empty and not df_mark_cap.empty:
    df_a_return = df_profit.div(df_mark_cap)
    df_a_return.index = ["Annual Yield (Return)"]
    calc_list.append(df_a_return)

# FCF Growth Rate
# FCF Growth Rate = Free cash flow (FCF)_Free Cash Flow
df_fcf = self._dataframe_slice(
    df_pivot, "Free cash flow (FCF)_Free Cash Flow"
).reset_index(drop=True)
fcf_gr_list = df_fcf.values.tolist()[0]

growth_rate = []
for gr in range(1, len(fcf_gr_list)):
    if fcf_gr_list[gr - 1] != 0:
        gnumbers = (
            (fcf_gr_list[gr] - fcf_gr_list[gr - 1])
            / fcf_gr_list[gr - 1]
            * 100
        )
    else:
        gnumbers = None
    growth_rate.append(gnumbers)
growth_rate.insert(0, None)
df_fcf_gr = pd.DataFrame(growth_rate).transpose()
df_fcf_gr.columns = list(df_fcf.columns)
df_fcf_gr.index = ["Free cash flow (FCF)"]
calc_list.append(df_fcf_gr)

# Dividend Payment
# Dividend Payment = if there has been dividend payment
df_div_payment = np.where(
    (
        self._dataframe_slice(
            df_pivot, "Dividend (adjusted) ps_Per Share Values"
        )
        > 0
    ),
    "yes",
    "no",
)
df_div_payment = pd.DataFrame(df_div_payment, columns=df_pivot.columns)
df_div_payment.index = ["Dividend Payment"]
calc_list.append(df_div_payment)

# Dividend Cover
# TODO

# Calculate DCF Intrinsic Value
intrinsic_value_list = []
base_year_fcf = self._dataframe_slice(
    df_pivot, "Free cash flow (FCF)_Free Cash Flow"
)
shares_outstanding = self._dataframe_slice(
    df_pivot, "Average shares (diluted)_Other"
)
growth_rate = self.df_dcf_variables[
    self.df_dcf_variables.param_name == ("Estimated Growth Rate")
]
longterm_growth_rate = self.df_dcf_variables[
    self.df_dcf_variables.param_name == ("Estimated Long Term Growth Rate")
]
discount_rate = self.df_dcf_variables[
    self.df_dcf_variables.param_name == "Estimated Discount Rate"
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
calc_list.append(df_dcf_intrinsic_value)

# Share Price
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
                price_list.append(share_price_slice.values[0][1] / 100)
                date_list.append(date)
                break
    else:
        price_list.append(share_price_slice.values[0][1] / 100)
        date_list.append(share_price_slice.values[0][3])

df_share_price_reduced = pd.DataFrame(data=price_list).transpose()
df_share_price_reduced.columns = date_list
if not df_share_price_reduced.empty:
    df_share_price_reduced.index = ["Share Price"]
    calc_list.append(df_share_price_reduced)

# Revenue Growth
revenue_growth_list = []
year_count = 0
row_title = "Turnover_Continuous Operatings"
# TODO add in banks and insurance companies
if not self._dataframe_slice(df_pivot, row_title).empty:
    df_turnover = self._dataframe_slice(df_pivot, row_title)
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
    calc_list.append(df_revenue_growth)

# EPS Growth
eps_growth_list = []
year_count = 0
row_title = "EPS norm. continuous_Per Share Values"

df_eps = self._dataframe_slice(df_pivot, row_title)
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
    calc_list.append(df_eps_growth)

# Dividend Growth
div_growth_list = []
year_count = 0
row_title = "Dividend (adjusted) ps_Per Share Values"

df_div = self._dataframe_slice(df_pivot, row_title)
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
    calc_list.append(df_div_growth)

# Growth Quality
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
    calc_list.append(df_growth_quality)

# Revenue Growth (10 year)
turnover_list = []
rev_growth_list = []
year_count = 0
row_title = "Turnover_Continuous Operatings"

# TODO add in banks and insurance companies
if not self._dataframe_slice(df_pivot, row_title).empty:
    df_turnover = self._dataframe_slice(df_pivot, row_title)
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
            rev_growth_year = (
                (last_three_years / first_three_years) - 1
            ) * 100
            rev_growth_list.append(rev_growth_year)

            # Remove first
            turnover_list.pop(0)
else:
    rev_growth_list = [None] * df_pivot.shape[1]

df_rev_growth_10 = pd.DataFrame(data=rev_growth_list).transpose()
df_rev_growth_10.columns = list(df_pivot.columns)
if not df_rev_growth_10.empty:
    df_rev_growth_10.index = ["Revenue Growth (10 year)"]
    calc_list.append(df_rev_growth_10)

# Earnings Growth (10 year)
eps_list = []
eps_growth_list = []
year_count = 0
row_title = "EPS norm. continuous_Per Share Values"

df_eps = self._dataframe_slice(df_pivot, row_title)
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
            eps_growth_year = (
                (last_three_years / first_three_years) - 1
            ) * 100
        else:
            eps_growth_year = 0
        eps_growth_list.append(eps_growth_year)

        # Remove first
        eps_list.pop(0)

df_eps_growth_10 = pd.DataFrame(data=eps_growth_list).transpose()
df_eps_growth_10.columns = list(df_pivot.columns)
if not df_eps_growth_10.empty:
    df_eps_growth_10.index = ["Earnings Growth (10 year)"]
    calc_list.append(df_eps_growth_10)

# Dividend Growth (10 year)
div_list = []
div_growth_list = []
year_count = 0
row_title = "Dividend (adjusted) ps_Per Share Values"

df_div = self._dataframe_slice(df_pivot, row_title)
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
            div_growth_year = (
                (last_three_years / first_three_years) - 1
            ) * 100
        div_growth_list.append(div_growth_year)

        # Remove first
        div_list.pop(0)

df_div_growth_10 = pd.DataFrame(data=div_growth_list).transpose()
df_div_growth_10.columns = list(df_pivot.columns)
if not df_div_growth_10.empty:
    df_div_growth_10.index = ["Dividend Growth (10 year)"]
    calc_list.append(df_div_growth_10)

# Overall Growth (10 year) &
# Growth Rate (10 year)
df_growth_rates = pd.concat(
    [df_rev_growth_10, df_eps_growth_10, df_div_growth_10]
)

df_overall_growth = pd.DataFrame(df_growth_rates.mean(axis=0)).transpose()
df_overall_growth.columns = list(df_pivot.columns)
if not df_overall_growth.empty:
    df_overall_growth.index = ["Overall Growth (10 year)"]
    calc_list.append(df_overall_growth)

# Replace any values over -100 with -100
# as this would produce imaginary numbers (NaN)
df_overall_growth[df_overall_growth < -100] = -100

# Calculate Rate
df_growth_rate = (pow((1 + (df_overall_growth / 100)), (1 / 7)) - 1) * 100
df_growth_rate.index = ["Growth Rate (10 year)"]
calc_list.append(df_growth_rate)

# print(df_growth_rates)
# print(df_overall_growth)
# print(df_growth_rate)

# Capital Employed
ce_list = []
year_count = 0

row_title = "Total assets_Assets"
df_assets = self._dataframe_slice(df_pivot, row_title)
row_title = "Current liabilities_Liabilities"

# TODO add in banks and insurance companies
if not self._dataframe_slice(df_pivot, row_title).empty:
    df_liabilities = self._dataframe_slice(df_pivot, row_title)

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
    calc_list.append(df_ce)

# ROCE
row_title = "Profit for financial year_Continuous Operatings"
if not self._dataframe_slice(df_pivot, row_title).empty:
    df_profit = self._dataframe_slice(df_pivot, row_title).reset_index(
        drop=True
    )
    df_roce = df_profit.div(df_ce.reset_index(drop=True)) * 100
else:
    roce_list = [None] * df_pivot.shape[1]
    df_roce = pd.DataFrame(data=roce_list).transpose()
    df_roce.columns = list(df_pivot.columns)

if not df_roce.empty:
    df_roce.index = ["ROCE"]
    calc_list.append(df_roce)

# Median ROCE (10 year)
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
    calc_list.append(df_roce_median)

# Debt Ratio
profit_list = []
debt_ratio_list = []
year_count = 0
row_title = "Short term borrowing_Liabilities"
if not self._dataframe_slice(df_pivot, row_title).empty:
    df_short_borrowing = self._dataframe_slice(df_pivot, row_title)

    row_title = "Profit for financial year_Continuous Operatings"
    df_profit = self._dataframe_slice(df_pivot, row_title)
    row_title = "Short term borrowing_Liabilities"
    df_short_borrowing = (
        self._dataframe_slice(df_pivot, row_title)
        .reset_index(drop=True)
        .fillna(0)
    )
    row_title = "Long term borrowing_Liabilities"
    df_long_borrowing = (
        self._dataframe_slice(df_pivot, row_title)
        .reset_index(drop=True)
        .fillna(0)
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
                yearly_debt_ratio = (
                    current_year_borrowing / statistics.mean(profit_list)
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
    calc_list.append(df_debt_ratio)

# Fill in the missing dates for share price
df_calculated = pd.concat(calc_list)

# PE10
eps_list = []
ep10_list = []
year_count = 0
row_title = "EPS norm. continuous_Per Share Values"
if not self._dataframe_slice(df_pivot, row_title).empty:
    df_eps = self._dataframe_slice(df_pivot, row_title)

    row_title = "Share Price"
    if not self._dataframe_slice(df_calculated, row_title).empty:
        df_share_price = self._dataframe_slice(df_calculated, row_title)

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
                    (current_year_share_price / statistics.mean(eps_list))
                    * 100
                )

                # Remove first
                eps_list.pop(0)
    else:
        ep10_list = [None] * df_pivot.shape[1]

df_pe10 = pd.DataFrame(data=ep10_list).transpose()
df_pe10.columns = list(df_pivot.columns)
if not df_pe10.empty:
    df_pe10.index = ["PE10"]
    calc_list.append(df_pe10)

# DP10
div_list = []
dp10_list = []
year_count = 0
row_title = "Dividend (adjusted) ps_Per Share Values"
if not self._dataframe_slice(df_pivot, row_title).empty:
    df_div = self._dataframe_slice(df_pivot, row_title)

    row_title = "Share Price"
    if not self._dataframe_slice(df_calculated, row_title).empty:
        df_share_price = self._dataframe_slice(df_calculated, row_title)

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
                        (
                            current_year_share_price
                            / statistics.mean(div_list)
                        )
                        * 100
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
    calc_list.append(df_dp10)

# Merge all dataframes
df_calculated = pd.concat(calc_list)

# if company_tidm == 'BRBY':
#     print(df_calculated)
#     print('STOP')

# Save to database
# Generate parameter_id and replace index
param_id_list = []
param_list = df_calculated.index
for param in param_list:

    param_id = self.df_params[self.df_params.param_name == param].id.values[
        0
    ]
    param_id_list.append(param_id)

df_calculated.index = param_id_list

# company id
company_id = self.df_companies[
    self.df_companies["tidm"] == company_tidm
].id.values[0]

# Create list of columns
df_items = df_calculated.items()
output_list = []
for label, content in df_items:
    output_list.append([content])

# Build SQL statement
sql = self._sql_builder()

# Get data from all columns and populate database
num_col = df_calculated.shape[1]

# Iterate over date columns
for i in range(0, num_col):

    current_col = output_list[i]
    data = current_col[0]

    # Get data for insert
    # Date of current report
    current_date = str(data.name)

    # Iterate over data to insert into database
    for index, value in data.items():

        # Check value format
        value = str(value)
        if value == "nan":
            value = None

        row = [
            str(company_id),
            index,
            current_date,
            value,
        ]

        self.cursor.execute(sql, row)
        self.db.commit()