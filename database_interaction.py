import os
from mysql_datalink import MysqlDatalink
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from datetime import timedelta, datetime
import math
import statistics


db_username = os.environ['DJANGO_DB_USERNAME']
db_password = os.environ['DJANGO_DB_PASSWORD']
db_name = os.environ['DJANGO_DB_NAME']


class DatabaseInteraction(MysqlDatalink):
    """A class to pull device list from database."""

    def __init__(self, table_name):
        """Initialize attributes of a device query."""
        self.table_name = table_name

        # Import csv template
        self._import_csv()
        super().__init__()

    def populate_static_table(self):
        """Insert static tables into database"""

        # Create table if not exists
        self._init_table()

        # Create sql
        sql = self._sql_builder()

        # Populate database
        iterator_table = self.df.iterrows()
        while True:
            try:
                row = next(iterator_table)[1].tolist()
                row = [str(i) for i in row]
                del row[0]
                self.cursor.execute(sql, row)
                self.db.commit()

            # if there are no more values in iterator, break the loop
            except StopIteration:
                break

    def populate_data_table(self):
        """Insert report data into database"""

        # Create table if not exists
        self._init_table()

        # Get the associated tables to get ids
        self._import_id_tables()

        # Import each file, process and save to database
        # Get list of reports
        path = "data/company_reports"
        file_list = []
        for files in os.listdir(path):
            file_list.append(files)
        num_files = len(file_list)
        file_num = 0

        for current_company_filename in file_list:
            file_num = file_num + 1
            s = f"file {file_num} of {num_files}, {current_company_filename}"
            print(s)

            # Get current report type
            filename_first = current_company_filename.split("_")[2]
            filename_second = current_company_filename.replace(".csv", "").split("_")[3]
            current_report_type = f"{filename_first} {filename_second}"

            # Get company tidm for associated id
            current_company_tidm = current_company_filename.split("_")[1]

            # Get last param name in section
            report_section_last_df = self.df_params[
                self.df_params.report_name == current_report_type.title()
            ]
            report_section_last_df = report_section_last_df[
                "report_section_last"
            ].unique()
            report_section_last_list = report_section_last_df.tolist()

            # Get company report data
            df_data = pd.read_csv(
                f"data/company_reports/{current_company_filename}",
                index_col="Period Ending",
                skiprows=1,
            )
            df_data = df_data.where((pd.notnull(df_data)), None)
            df_data = df_data.drop("Result Type", axis=0)
            if " " in df_data.index:
                df_data = df_data.drop(" ")

            # Generate parameter_id and replace index
            i_section = 0
            i_param = 0
            param_id_list = []

            param_list = df_data.index

            for section in report_section_last_list:

                param_section_filter_list_df = self.df_params[
                    self.df_params.report_section_last == section
                ]

                while True:

                    param_id = param_section_filter_list_df[
                        (param_section_filter_list_df.param_name == param_list[i_param])
                    ]
                    param_id = param_id.iloc[0]["id"]
                    param_id_list.append(param_id)

                    if param_list[i_param] == section:
                        i_section = i_section + 1
                        i_param = i_param + 1
                        break

                    i_param = i_param + 1

            df_data.index = param_id_list

            # company id
            company_id = self.df_companies[
                self.df_companies["tidm"] == current_company_tidm
            ].id.values[0]

            # Create list of columns
            df_items = df_data.items()
            output_list = []
            for label, content in df_items:
                output_list.append([content])

            # Build SQL statement
            sql = self._sql_builder()

            # Get data from all columns and populate database
            num_col = df_data.shape[1]

            # Date formats
            date_fmts = ("%d/%m/%Y %H:%M:%S", "%d/%m/%y %H:%M:%S")

            # Iterate over date columns
            for i in range(0, num_col):

                current_col = output_list[i]
                data = current_col[0]

                # Get data for insert
                # Date of current report
                current_date = f"{data.name} 00:00:00"

                # Iterate over data to insert into database
                i = 0
                for index, value in data.items():
                    i = i + 1

                    # Check value format
                    if value == "Infinity" or value == "-Infinity":
                        value = None

                    # Check datetime format
                    for fmt in date_fmts:
                        try:
                            current_date_time = datetime.strptime(current_date, fmt)
                            break
                        except ValueError as err:
                            pass

                    row = [
                        str(company_id),
                        index,
                        current_date_time,
                        value,
                    ]

                    self.cursor.execute(sql, row)
                    self.db.commit()

    def populate_share_price_table(self):
        """Calculate data and insert share price data into database"""

        # Create table if not exists
        self._init_table()

        # Get the associated tables to get ids
        self._import_id_tables()

        # Get list of reports
        path = "data/share_prices"
        file_list = []
        for files in os.listdir(path):
            file_list.append(files)
        num_files = len(file_list)
        # file_list

        # Import each file, process and save to database
        file_num = 0
        for current_company_filename in file_list:
            file_num = file_num + 1
            print(f"file {file_num} of {num_files}, {current_company_filename}")

            # Get company tidm for associated id
            current_company_tidm = current_company_filename.split("_")[1]

            # Get company report data
            df_data = pd.read_csv(
                f"data/share_prices/{current_company_filename}"
                )
            df_data = df_data.where((pd.notnull(df_data)), None)

            ## New Section
            # company id
            company_id = self.df_companies[
                self.df_companies["tidm"] == current_company_tidm
            ].id.values[0]

            # Format dataframe to database schema
            df_data.insert(0, "company_id", [company_id] * df_data.shape[0])
            df_data = df_data.drop(["Open", "High", "Low"], axis=1)
            df_data.rename(
                columns={
                    "Date": "time_stamp",
                    "Close": "value",
                    "Volume": "volume",
                    "Adjustment": "adjustment",
                },
                inplace=True,
            )

            ## New Section
            # Build sql query
            sql = self._sql_builder()

            # Populate database
            for index, row in df_data.iterrows():
                row_list = [
                    row[0],
                    datetime.strptime(
                        f"{row[1]} 00:00:00", "%d/%m/%Y %H:%M:%S"
                        ),
                    row[2],
                    row[3],
                    row[4],
                ]
                self.cursor.execute(sql, row_list)
                self.db.commit()

    def populate_calculated_table(self):
        """Calculate data and insert report data into database"""

        # Create table if not exists
        self._init_table()

        # Get the associated tables to get ids
        self._import_id_tables()

        # Calculate values for each company
        # Get list of companies
        company_list = self.df_companies.tidm.to_list()
        num_companies = len(company_list)
        company_num = 0

        for company_tidm in company_list:
            company_num = company_num + 1
            print(f"Company {company_num} of {num_companies}, {company_tidm}")

            df_share_price = self._import_share_data(company_tidm)

            # Get Report Data
            self.cursor.execute(
                "SELECT param_name, report_section, time_stamp, value "
                "FROM reporting_data LEFT JOIN companies "
                "ON reporting_data.company_id = companies.id "
                "LEFT JOIN parameters "
                "ON reporting_data.parameter_id = parameters.id "
                "LEFT JOIN report_section "
                "ON parameters.report_section_id = report_section.id "
                f"WHERE tidm = '{company_tidm}'"
            )

            data = self.cursor.fetchall()

            # Add parameter names to index
            data_list = []

            # Convert to list from tuple
            for data_item in data:
                data_list.append(list(data_item))

            # Add unique column name merging param name and report section
            for data_item in data_list:
                data_item.append(f"{data_item[0]}_{data_item[1]}")

            col_names_list = [
                "param_name",
                "report_section",
                "time_stamp",
                "value",
                "param_name_report_section",
            ]
            df = pd.DataFrame(data_list, columns=col_names_list)

            # Pivot dataframe
            df_pivot = df.pivot(
                columns="time_stamp", index="param_name_report_section", values="value"
            )
            df_pivot = df_pivot.astype(float)

            # Calculations
            calc_list = []

            # Debt to Equity (D/E) =
            # Balance Sheet Total liabilities_Liabilities
            # / Total equity_Equity
            df_tl = self._dataframe_slice(
                df_pivot, "Total liabilities_Liabilities"
            ).reset_index(drop=True)
            df_te = self._dataframe_slice(df_pivot, "Total equity_Equity").reset_index(
                drop=True
            )
            df_d_e = df_tl.div(df_te)
            df_d_e.index = ["Debt to Equity (D/E)"]
            calc_list.append(df_d_e)

            # Current Ratio =
            # Current assets_Assets
            # / Current liabilities_Liabilities
            df_ca = self._dataframe_slice(
                df_pivot, "Current assets_Assets"
            ).reset_index(drop=True)
            df_cl = self._dataframe_slice(
                df_pivot, "Current liabilities_Liabilities"
            ).reset_index(drop=True)
            if not df_ca.empty and not df_cl.empty:
                df_cr = df_ca.div(df_cl)
                df_cr.index = ["Current Ratio"]
                calc_list.append(df_cr)

            # Return on Equity (ROE) =
            # Profit for financial year_Continuous Operatings
            # / Shareholders funds (NAV)_Equity
            df_profit = self._dataframe_slice(
                df_pivot, "Profit for financial year_Continuous Operatings"
            ).reset_index(drop=True)
            df_nav = self._dataframe_slice(
                df_pivot, "Shareholders funds (NAV)_Equity"
            ).reset_index(drop=True)
            if not df_profit.empty and not df_nav.empty:
                df_roe = df_profit.div(df_nav)
                df_roe.index = ["Return on Equity (ROE)"]
                calc_list.append(df_roe)

            # Equity (Book Value) Per Share =
            # Shareholders funds (NAV)_Equity
            # / Average shares (diluted)_Other
            df_nav = self._dataframe_slice(
                df_pivot, "Shareholders funds (NAV)_Equity"
            ).reset_index(drop=True)
            df_shares = self._dataframe_slice(
                df_pivot, "Average shares (diluted)_Other"
            ).reset_index(drop=True)
            if not df_nav.empty and not df_shares.empty:
                df_eps = df_nav.div(df_shares)
                df_eps.index = ["Equity (Book Value) Per Share"]
                calc_list.append(df_eps)

            # Price to Earnings (P/E) =
            # Market capitalisation_Other
            # / Profit for financial year_Continuous Operatings
            df_mark_cap = self._dataframe_slice(
                df_pivot, "Market capitalisation_Other"
            ).reset_index(drop=True)
            df_profit = self._dataframe_slice(
                df_pivot, "Profit for financial year_Continuous Operatings"
            ).reset_index(drop=True)
            if not df_mark_cap.empty and not df_profit.empty:
                df_ppe = df_mark_cap.div(df_profit)
                df_ppe.index = ["Price to Earnings (P/E)"]
                calc_list.append(df_ppe)

            # Price to Book Value (Equity) =
            # Market capitalisation_Other
            # / Average shares (diluted)_Other
            df_mark_cap = self._dataframe_slice(
                df_pivot, "Market capitalisation_Other"
            ).reset_index(drop=True)
            df_shares = self._dataframe_slice(
                df_pivot, "Average shares (diluted)_Other"
            ).reset_index(drop=True)
            if not df_mark_cap.empty and not df_shares.empty:
                df_pbv = df_mark_cap.div(df_shares)
                df_pbv.index = ["Price to Book Value (Equity)"]

            df_equity = self._dataframe_slice(
                df_pbv, "Price to Book Value (Equity)"
            ).reset_index(drop=True)
            df_eps = self._dataframe_slice(
                df_eps, "Equity (Book Value) Per Share"
            ).reset_index(drop=True)
            if not df_equity.empty and not df_eps.empty:
                df_pbv = df_equity.div(df_eps)
                df_pbv.index = ["Price to Book Value (Equity)"]

            calc_list.append(df_pbv)

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

    def populate_ranking_table(self):
        """Calculate data and insert report data into database"""

        # Create table if not exists
        self._init_table()

        # Get the associated tables to get ids
        self._import_id_tables()

        # Calculate rank for each type
        ranktype_list = [
            "Growth Rate (10 year)",
            "Growth Quality",
            "Median ROCE (10 year)",
            "PE10",
            "DP10",
        ]

        rank_df_list = []
        values_df_list = []
        num_ranks = len(ranktype_list)
        rank_num = 0

        for rank_type in ranktype_list:

            print(f"Rank {rank_num + 1} of {num_ranks}, {rank_type}")

            # Get Calculated Data
            self.cursor.execute(
                "SELECT time_stamp, value, tidm FROM calculated_data "
                "LEFT JOIN companies "
                "ON calculated_data.company_id = companies.id "
                "LEFT JOIN parameters "
                "ON calculated_data.parameter_id = parameters.id "
                f"WHERE param_name = '{rank_type}'"
            )
            data = self.cursor.fetchall()

            # Create Dataframe
            df = pd.DataFrame(data, columns=["time_stamp", "value", "tidm"])

            # Offset dates by 1 day to account for companies
            # reporting on first of the year
            df["time_stamp_delta"] = df["time_stamp"] + pd.DateOffset(days=-1)
            df["year"] = pd.DatetimeIndex(df["time_stamp_delta"]).year

            # Show duplicate rows
            # duplicated_columns_df = df[
            # df.duplicated(subset=['tidm', 'year'
            # ], keep=False)]
            # duplicated_columns_df

            # Remove Duplicates and take last value
            # This accounts for companies reporting
            # twice in a year and take last report
            df2 = df.drop_duplicates(subset=["tidm", "year"], keep="last")

            # Pivot dataframe
            df_pivot = (
                df2.pivot(columns="year", index="tidm", values="value")
                .replace(to_replace="None", value=None)
                .astype("float")
            )
            # df_pivot

            # Create Growth list
            last_list = []
            tidm_list = df_pivot.index

            # Get last value if exists,
            # if not, then take second to last
            for i, row in df_pivot.iterrows():
                current_value = row.values[df_pivot.shape[1] - 1]

                if math.isnan(current_value):
                    current_value = row.values[df_pivot.shape[1] - 2]

                last_list.append(current_value)

            # Convert to dataframe
            df_growth_values = pd.DataFrame(data=last_list)
            df_growth_values.columns = [f"{ranktype_list[rank_num]} Rank Value"]
            df_growth_values.index = tidm_list

            # Replace NaN with -999
            df_growth_values = df_growth_values.fillna(-999)
            if ranktype_list[rank_num] == "PE10" or ranktype_list[rank_num] == "DP10":
                mask = df_growth_values[f"{ranktype_list[rank_num]} Rank Value"].gt(0)
                df_growth_values = pd.concat(
                    [
                        df_growth_values[mask].sort_values(
                            f"{ranktype_list[rank_num]} Rank Value"
                        ),
                        df_growth_values[~mask].sort_values(
                            f"{ranktype_list[rank_num]} Rank Value", ascending=False
                        ),
                    ]
                )
            else:
                df_growth_values = df_growth_values.sort_values(
                    by=f"{ranktype_list[rank_num]} Rank Value", ascending=False
                )

            # Rank Dataframe
            df_growth_rank = pd.DataFrame()
            df_growth_rank[f"{ranktype_list[rank_num]} Rank"] = range(
                len(df_growth_values)
            )
            df_growth_rank.index = df_growth_values.index

            values_df_list.append(df_growth_values)
            rank_df_list.append(df_growth_rank)

            rank_num = rank_num + 1

        df_growth_values = pd.concat(values_df_list, axis=1)

        # Growth Rank
        df_growth_rank = pd.concat(rank_df_list, axis=1)
        df_growth_rank["Defensive Rank"] = df_growth_rank.sum(axis=1)
        df_growth_rank = df_growth_rank.sort_values(by="Defensive Rank", ascending=True)

        # Combine back together
        df_rank_both = pd.concat([df_growth_values, df_growth_rank], axis=1)

        # Save to database
        # Generate parameter_id and replace index
        param_id_list = []
        param_list = df_rank_both.columns
        for param in param_list:

            param_id = self.df_params[self.df_params.param_name == param].id.values[0]
            param_id_list.append(param_id)

        df_rank_both.columns = param_id_list

        # company id
        company_id_list = []
        company_list = df_rank_both.index
        for company in company_list:

            company_id = self.df_companies[self.df_companies.tidm == company].id.values[
                0
            ]
            company_id_list.append(company_id)

        df_rank_both.index = company_id_list

        # Create list of columns
        df_items = df_rank_both.items()
        output_list = []
        for label, content in df_items:
            output_list.append([content])

        time_stamp_now = datetime.now()

        # Build SQL statement
        sql = self._sql_builder()

        # Get data from all columns and populate database
        num_col = df_rank_both.shape[1]

        # Iterate over date columns
        for i in range(0, num_col):

            current_col = output_list[i]
            data = current_col[0]

            # Get data for insert
            # Date of current report
            current_parameter_id = str(data.name)

            # Iterate over data to insert into database
            for index, value in data.items():

                row = [
                    str(index),
                    current_parameter_id,
                    time_stamp_now,
                    str(value),
                ]

                self.cursor.execute(sql, row)
                self.db.commit()

    def get_data(self):
        """Get data from the database"""

        self.cursor.execute(f"SELECT * FROM {self.table_name}")
        rows = self.cursor.fetchall()
        get_col_names_list = self.col_names_list.copy()
        get_col_names_list.insert(0, "id")
        df = pd.DataFrame(rows, columns=get_col_names_list)
        return df

    def _init_table(self):
        """Initialise table"""

        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {self.table_name} \
                ({self.sql_col_names})"
        )
        self.db.commit()

    def _import_csv(self):
        self.df = pd.read_csv(f"data/database_tables/{self.table_name}.csv")

        # column names and sql builder
        sql_col_names = []
        col_names_list = []

        for col in self.df.columns:
            sql_col_names.append(col)
            col_names_list.append(col.split(" ")[0])
        del col_names_list[0]

        self.col_names_list = col_names_list
        self.sql_col_names = ", ".join(sql_col_names)

    def _import_id_tables(self):
        # Get params table data for associated id
        # Connection string for sqlalchemy
        db_connection_str = (
            f"mysql://{db_username}:{db_password}@localhost/{db_name}"
        )

        # Connect to database
        db_connection = create_engine(db_connection_str)

        # Read params data
        self.df_params = pd.read_sql(
            ("SELECT parameters.id, param_name, report_section, "
             "report_section_last, report_name FROM parameters "
             "LEFT JOIN report_section "
             "ON parameters.report_section_id = report_section.id "
             "LEFT JOIN report_type "
             "ON report_section.report_type_id = report_type.id"),
            con=db_connection,
        )

        # Read companies data
        self.df_companies = pd.read_sql(
            "SELECT * FROM companies", con=db_connection
            )

        self.df_dcf_variables = pd.read_sql(
            ("SELECT param_name, value FROM calc_variables "
             "LEFT JOIN parameters "
             "ON calc_variables.parameter_id = parameters.id"),
            con=db_connection,
        )

        # Close connection
        db_connection.dispose()

    def _import_share_data(self, company_tidm):
        # Get params table data for associated id
        # Connection string for sqlalchemy
        db_connection_str = (
            f"mysql://{db_username}:{db_password}@localhost/{db_name}"
        )

        # Connect to database
        db_connection = create_engine(db_connection_str)

        # Get Share Price data
        df_share_price = pd.read_sql(
            ("SELECT tidm, price, volume, time_stamp "
             "FROM share_price LEFT JOIN companies "
             "ON share_price.company_id = companies.id "
             f"WHERE tidm = '{company_tidm}'"),
            con=db_connection,
        )

        # Close connection
        db_connection.dispose()

        return df_share_price

    def _sql_builder(self):
        placeholders = ", ".join(["%s"] * len(self.col_names_list))
        columns = ", ".join(self.col_names_list)
        sql = f"INSERT INTO {self.table_name} \
            ( {columns} ) VALUES ( {placeholders} )"
        return sql

    def _dataframe_slice(self, df_input, row_title):
        try:
            result = df_input[row_title:row_title]
            return result
        except KeyError:
            return pd.DataFrame()
