from django.core.management.base import BaseCommand

from portfolio.models import Portfolio, Transactions
from ancillary_info.models import Companies
from dashboard_company.models import DashboardCompany


import pandas as pd
import numpy as np


class Command(BaseCommand):
    help = "Generates portfolio stats"

    def handle(self, *args, **kwargs):
        num_rows_created = 0
        num_rows_updated = 0

        # Transaction Info
        transaction_df = self._get_portfolio_data()
        transaction_sum_df = transaction_df.groupby(["company__tidm", "decision__value"]).sum()
        transaction_sum_df = transaction_sum_df.reset_index()

        df_dashboard = pd.DataFrame(list(DashboardCompany.objects.get_table_joined()))

        tidm_list = transaction_df['company__tidm'].unique()
        num_companies = len(tidm_list)

        company_num = 0
        idx = 0
        buy_text = 'Bought'
        sell_text = 'Sold'
        results_list = []

        for tidm in tidm_list:
            company_num = company_num + 1
            print(f"Company {company_num} of {num_companies}, {tidm}")

            # Latest Share Holding
            dash_idx = df_dashboard[df_dashboard["tidm"] == tidm].index[0]
            latest_share_price = df_dashboard["latest_share_price"].iat[dash_idx]
            curr_comp_name = df_dashboard["company_name"].iat[dash_idx]
            comp_id = df_dashboard["company_id"].iat[dash_idx]
            results_list.append({
                "tidm": tidm,
                "company_name": curr_comp_name,
                "comp_id": comp_id,
                "latest_share_price": f"{latest_share_price:.2f}"
                })

            # Number of shares
            num_shares_bought = transaction_sum_df[(transaction_sum_df['company__tidm'] == tidm) & (transaction_sum_df['decision__value'] == buy_text)].num_stock.sum()
            num_shares_sold = transaction_sum_df[(transaction_sum_df['company__tidm'] == tidm) & (transaction_sum_df['decision__value'] == sell_text)].num_stock.sum()
            # TODO ############### Temp Testing, take out ###############
            # num_shares_holding = num_shares_bought - num_shares_sold
            latest_shares_num = num_shares_bought
            # ############## END ###############
            results_list[idx].update({"latest_shares_num": f"{latest_shares_num}"})
            latest_share_holding = latest_shares_num * latest_share_price
            results_list[idx].update({"latest_shares_holding": f"{latest_share_holding}"})

            # Fee for transaction
            fees_bought = transaction_sum_df[(transaction_sum_df['company__tidm'] == tidm) & (transaction_sum_df['decision__value'] == buy_text)].fees.sum()
            results_list[idx].update({"fees_bought": f"{fees_bought:.2f}"})
            fees_sold = transaction_sum_df[(transaction_sum_df['company__tidm'] == tidm) & (transaction_sum_df['decision__value'] == sell_text)].fees.sum()
            results_list[idx].update({"fees_sold": f"{fees_sold:.2f}"})
            fees_total = fees_bought + fees_sold
            results_list[idx].update({"fees_total": f"{fees_total:.2f}"})

            # Share cost for transaction
            initial_shares_holding = transaction_sum_df[(transaction_sum_df['company__tidm'] == tidm) & (transaction_sum_df['decision__value'] == buy_text)].price.sum()
            results_list[idx].update({"initial_shares_holding": f"{initial_shares_holding:.2f}"})

            # Total cost for transaction
            total_cost = initial_shares_holding + fees_bought
            results_list[idx].update({"initial_shares_cost": f"{total_cost:.2f}"})

            # Value and pct change
            share_value_change = latest_share_holding - initial_shares_holding
            results_list[idx].update({"share_value_change": f"{share_value_change:.2f}"})
            share_pct_change = ((latest_share_holding - initial_shares_holding) / initial_shares_holding) * 100
            results_list[idx].update({"share_pct_change": f"{share_pct_change:.2f}"})

            idx = idx + 1

        # Generate totals
        total_fees = 0
        total_initial_value = 0
        total_latest_value = 0
        total_dict = {}

        for item in results_list:
            # Create totals
            total_fees = total_fees + float(item['fees_total'])
            total_initial_value = total_initial_value + float(item['initial_shares_cost'])
            total_latest_value = total_latest_value + float(item['latest_shares_holding'])
            total_value_change = total_latest_value - total_initial_value
            total_pct_value_change = ((total_latest_value - total_initial_value) / total_initial_value) * 100
            pct_fees = (total_fees / (total_initial_value + total_fees)) * 100

        idx = 0
        for item in results_list:
            # Calculate company % in portfolio
            comp_latest_value = float(item['latest_shares_holding'])
            comp_pct_holding = (comp_latest_value / total_latest_value) * 100
            results_list[idx].update({"company_pct_holding": f"{comp_pct_holding:.2f}"})
            idx = idx + 1

        total_dict["total_initial_value"] = [total_initial_value]
        total_dict["total_fees"] = [total_fees]
        total_dict["total_pct_fees"] = [pct_fees]
        total_dict["total_latest_value"] = [total_latest_value]
        total_dict["total_value_change"] = [total_value_change]
        total_dict["total_pct_value_change"] = [total_pct_value_change]

        # Create Dataframes
        results_df = pd.DataFrame.from_records(results_list)
        total_df = pd.DataFrame.from_dict(total_dict, orient='columns')
        print(total_df)
        print(results_df)

        # Split ready for create or update
        [df_create, df_update] = self._create_update_split(results_df)

        # Create new companies
        if not df_create.empty:
            num_rows_created = self._create_rows(df_create)
            print(f"Portfolio Create Complete: {num_rows_created} rows updated")

        # Update existing companies
        if not df_update.empty:
            num_rows_updated = self._update_rows(df_update)
            print(f"Portfolio Update Complete: {num_rows_updated} rows updated")

        return f"Created: {str(num_rows_created)}, Updated: {str(num_rows_updated)}"

    def _get_portfolio_data(self):
        transaction_df = pd.DataFrame(list(Transactions.objects.get_table_joined()))

        transaction_df["price"] = transaction_df["price"].astype(float)
        transaction_df["fees"] = transaction_df["fees"].astype(float)

        return transaction_df

    def _create_update_split(self, new_df):
        existing_df = pd.DataFrame(list(Portfolio.objects.get_table_joined()))

        if not existing_df.empty:
            split_idx = np.where(
                new_df["tidm"].isin(existing_df["company__tidm"]), "existing", "new"
            )
            df_existing = new_df[split_idx == "existing"]
            df_new = new_df[split_idx == "new"]
        else:
            df_new = new_df
            df_existing = pd.DataFrame()

        return df_new, df_existing

    def _create_rows(self, df_create):
        # Save to database
        reports = [
            Portfolio(
                company=Companies.objects.get(id=row["comp_id"]),
                latest_share_price=row["latest_share_price"],
                latest_shares_num=row["latest_shares_num"],
                latest_shares_holding=row["latest_shares_holding"],
                fees_bought=row["fees_bought"],
                fees_sold=row["fees_sold"],
                fees_total=row["fees_total"],
                initial_shares_holding=row["initial_shares_holding"],
                initial_shares_cost=row["initial_shares_cost"],
                share_value_change=row["share_value_change"],
                share_pct_change=row["share_pct_change"],
                company_pct_holding=row["company_pct_holding"],
            )
            for i, row in df_create.iterrows()
        ]
        list_of_objects = Portfolio.objects.bulk_create(reports)

        total_rows_added = len(list_of_objects)

        return total_rows_added

    def _update_rows(self, df_update):

        companies = list(Portfolio.objects.all())
        num_companies = len(companies)
        company_num = 0
        total_rows = 0

        param_dict = {
            "industry_name": "industry__value",
            "revenue": "Total Revenue",
            "earnings": "Reported EPS",
            "dividends": "Dividends Per Share",
            "capital_expenditure": "Capital Expenditures",
            "net_income": "Net Income",
            "total_equity": "Total Equity",
            "share_price": "Share Price",
            "debt_to_equity": "Debt to Equity (D/E)",
            "current_ratio": "Current Ratio",
            "return_on_equity": "Return on Equity (ROE)",
            "equity_per_share": "Equity (Book Value) Per Share",
            "price_to_earnings": "Price to Earnings (P/E)",
            "price_to_equity": "Price to Book Value (Equity)",
            "earnings_yield": "Earnings Yield",
            "annual_yield_return": "Annual Yield (Return)",
            "fcf": "Free Cash Flow",
            "dividend_cover": "Dividend Cover",
            "capital_employed": "Capital Employed",
            "roce": "Return on Capital Employed (ROCE)",
            "dcf_intrinsic_value": "Intrinsic Value",
            "margin_safety": "Margin of Safety",
            "latest_margin_of_safety": "Latest Margin of Safety",
            "estimated_growth_rate": "Estimated Growth Rate",
            "estimated_discount_rate": "Estimated Discount Rate",
            "estimated_long_term_growth_rate": "Estimated Long Term Growth Rate",
            "market_cap": "Market Capitalisation",
            "pick_source": "company_source__value",
            "exchange_country": "country__value",
            "currency_symbol": "currency__symbol",
            "latest_share_price_date": "share_latest_date",
            "latest_share_price": "latest_share_price",
            "latest_financial_date": "financial_latest_date",
        }

        for index, company in enumerate(companies):

            # For each company, get the associated row in df
            df_update = df_update.reset_index(drop=True)
            cur_row = df_update[df_update["tidm"] == company.tidm].index[0]

            company_num = company_num + 1
            print(f"Company {company_num} of {num_companies}, {company.tidm}")

            if cur_row:
                companies[index].industry_name = df_update.loc[
                    df_update.index[cur_row], "industry__value"
                ]

                companies[index].revenue = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Total Revenue"]
                )

                companies[index].earnings = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Reported EPS"]
                )

                companies[index].dividends = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Dividends Per Share"]
                )

                companies[index].capital_expenditure = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Capital Expenditures"]
                )

                companies[index].net_income = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Net Income"]
                )

                companies[index].total_equity = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Total Equity"]
                )

                companies[index].share_price = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Share Price"]
                )

                companies[index].debt_to_equity = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Debt to Equity (D/E)"]
                )

                companies[index].current_ratio = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Current Ratio"]
                )

                companies[index].return_on_equity = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Return on Equity (ROE)"]
                )

                companies[index].equity_per_share = self._convert_float(
                    df_update.loc[
                        df_update.index[cur_row], "Equity (Book Value) Per Share"
                    ]
                )

                companies[index].price_to_earnings = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Price to Earnings (P/E)"]
                )

                companies[index].price_to_equity = self._convert_float(
                    df_update.loc[
                        df_update.index[cur_row], "Price to Book Value (Equity)"
                    ]
                )

                companies[index].earnings_yield = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Earnings Yield"]
                )

                companies[index].annual_yield_return = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Annual Yield (Return)"]
                )

                companies[index].fcf = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Free Cash Flow"]
                )

                companies[index].dividend_cover = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Dividend Cover"]
                )

                companies[index].capital_employed = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Capital Employed"]
                )

                companies[index].roce = self._convert_float(
                    df_update.loc[
                        df_update.index[cur_row], "Return on Capital Employed (ROCE)"
                    ]
                )

                companies[index].dcf_intrinsic_value = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Intrinsic Value"]
                )

                companies[index].margin_safety = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Margin of Safety"]
                )

                companies[index].latest_margin_of_safety = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Latest Margin of Safety"]
                )

                companies[index].estimated_growth_rate = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Estimated Growth Rate"]
                )

                companies[index].estimated_discount_rate = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Estimated Discount Rate"]
                )

                companies[index].estimated_long_term_growth_rate = self._convert_float(
                    df_update.loc[
                        df_update.index[cur_row], "Estimated Long Term Growth Rate"
                    ]
                )

                companies[index].pick_source = df_update.loc[
                    df_update.index[cur_row], "company_source__value"
                ]

                companies[index].exchange_country = df_update.loc[
                    df_update.index[cur_row], "country__value"
                ]

                companies[index].currency_symbol = df_update.loc[
                    df_update.index[cur_row], "currency__symbol"
                ]

                companies[index].latest_financial_date = df_update.loc[
                    df_update.index[cur_row], "financial_latest_date"
                ]

                companies[index].latest_share_price_date = df_update.loc[
                    df_update.index[cur_row], "share_latest_date"
                ]

                companies[index].latest_share_price = df_update.loc[
                    df_update.index[cur_row], "latest_share_price"
                ]

                companies[index].market_cap = self._convert_float(
                    df_update.loc[df_update.index[cur_row], "Market Capitalisation"]
                )

        print("Updating Dashboard Table")

        for key in param_dict:
            num_rows_updated = Portfolio.objects.bulk_update(companies, [key])
            total_rows = total_rows + num_rows_updated

        return total_rows

    def _convert_float(self, input):

        if pd.notnull(input):
            output = float(input)
        else:
            output = input

        return output
