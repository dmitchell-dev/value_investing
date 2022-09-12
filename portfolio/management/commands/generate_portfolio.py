from ast import AsyncFunctionDef
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
            latest_shares_num = num_shares_bought - num_shares_sold
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
            sold_shares_income = transaction_sum_df[(transaction_sum_df['company__tidm'] == tidm) & (transaction_sum_df['decision__value'] == sell_text)].price.sum()
            results_list[idx].update({"sold_shares_income": f"{sold_shares_income:.2f}"})

            # Total cost for transaction
            initial_shares_cost = initial_shares_holding + fees_bought
            results_list[idx].update({"initial_shares_cost": f"{initial_shares_cost:.2f}"})
            income_from_selling = sold_shares_income - fees_sold
            results_list[idx].update({"income_from_selling": f"{income_from_selling:.2f}"})

            # Profit
            total_profit = income_from_selling - initial_shares_cost
            results_list[idx].update({"total_profit": f"{total_profit:.2f}"})

            # Value and pct change
            share_value_change = latest_share_holding - initial_shares_cost
            results_list[idx].update({"share_value_change": f"{share_value_change:.2f}"})
            share_pct_change = ((latest_share_holding - initial_shares_cost) / initial_shares_cost) * 100
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
            if total_latest_value == 0:
                comp_pct_holding = 0
            else:
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
                sold_shares_income=row["sold_shares_income"],
                income_from_selling=row["income_from_selling"],
                total_profit=row["total_profit"],
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
            "latest_share_price": "latest_share_price",
            "latest_shares_num": "latest_shares_num",
            "latest_shares_holding": "latest_shares_holding",
            "fees_bought": "fees_bought",
            "fees_sold": "fees_sold",
            "fees_total": "fees_total",
            "initial_shares_holding": "initial_shares_holding",
            "sold_shares_income": "sold_shares_income",
            "income_from_selling": "income_from_selling",
            "total_profit": "total_profit",
            "initial_shares_cost": "initial_shares_cost",
            "share_value_change": "share_value_change",
            "share_pct_change": "share_pct_change",
            "company_pct_holding": "company_pct_holding",
        }

        for index, company in enumerate(companies):

            # For each company, get the associated row in df
            df_update = df_update.reset_index(drop=True)
            cur_row = df_update[df_update["comp_id"] == company.pk].index[0]

            company_num = company_num + 1
            print(f"Company {company_num} of {num_companies}, {df_update['tidm']}")

            companies[index].latest_share_price = df_update.loc[
                df_update.index[cur_row], "latest_share_price"
            ]

            companies[index].latest_shares_num = self._convert_float(
                df_update.loc[df_update.index[cur_row], "latest_shares_num"]
            )

            companies[index].latest_shares_holding = self._convert_float(
                df_update.loc[df_update.index[cur_row], "latest_shares_holding"]
            )

            companies[index].fees_bought = self._convert_float(
                df_update.loc[df_update.index[cur_row], "fees_bought"]
            )

            companies[index].fees_sold = self._convert_float(
                df_update.loc[df_update.index[cur_row], "fees_sold"]
            )

            companies[index].fees_total = self._convert_float(
                df_update.loc[df_update.index[cur_row], "fees_total"]
            )

            companies[index].initial_shares_holding = self._convert_float(
                df_update.loc[df_update.index[cur_row], "initial_shares_holding"]
            )

            companies[index].sold_shares_income = self._convert_float(
                df_update.loc[df_update.index[cur_row], "sold_shares_income"]
            )

            companies[index].income_from_selling = self._convert_float(
                df_update.loc[df_update.index[cur_row], "income_from_selling"]
            )

            companies[index].total_profit = self._convert_float(
                df_update.loc[df_update.index[cur_row], "total_profit"]
            )

            companies[index].initial_shares_cost = self._convert_float(
                df_update.loc[df_update.index[cur_row], "initial_shares_cost"]
            )

            companies[index].share_value_change = self._convert_float(
                df_update.loc[df_update.index[cur_row], "share_value_change"]
            )

            companies[index].share_pct_change = self._convert_float(
                df_update.loc[df_update.index[cur_row], "share_pct_change"]
            )

            companies[index].company_pct_holding = self._convert_float(
                df_update.loc[df_update.index[cur_row], "company_pct_holding"]
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
