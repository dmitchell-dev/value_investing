from django.db.models import QuerySet

import plotly.express as px
from plotly.offline import plot


class TransactionsQueryset(QuerySet):
    def get_table_joined(self):
        return self.values(
            "num_stock",
            "decision",
            "reference",
            "price",
            "fees",
            "created_at",
            "date_dealt",
            "date_settled",
            "company",
            "company__tidm",
            "company__company_name",
            "company__industry",
            "company__sector",
            "company__exchange",
            "company__country",
            "company__currency",
            "decision__value",
        )


class CashQueryset(QuerySet):
    def get_table_joined(self):
        return self.values(
            "decision",
            "cash_value",
            "created_at",
            "date_dealt",
            "decision__value",
        )


class WishListQueryset(QuerySet):
    def get_table_joined(self):
        return self.values(
            "current_mos",
            "buy_mos",
            "company__tidm",
            "company__company_name",
        )


class PortfolioQueryset(QuerySet):
    def get_table_joined(self):
        return self.values(
            "latest_share_price",
            "latest_shares_num",
            "latest_shares_holding",
            "fees_bought",
            "fees_sold",
            "fees_total",
            "initial_shares_holding",
            "initial_shares_cost",
            "income_from_selling",
            "total_profit",
            "share_value_change",
            "share_pct_change",
            "company_pct_holding",
            "sold_shares_income",
            "company",
            "company__tidm",
            "company__company_name",
        )


def value_pie_chart(portfolio_df):
    fig = px.pie(portfolio_df, values="latest_shares_holding", names="company__company_name")
    plot_div = plot(fig, output_type="div")

    return plot_div


def perf_bar_chart(tidm_list, pct_change_list):

    chart_dict = {}
    chart_dict["tidm"] = tidm_list
    chart_dict["pct_value_change"] = pct_change_list
    fig = px.bar(chart_dict, x="tidm", y="pct_value_change")

    plot_div2 = plot(fig, output_type="div")

    return plot_div2
