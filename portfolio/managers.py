from django.db.models import QuerySet

import plotly.express as px
from plotly.offline import plot


class InvestmentsQueryset(QuerySet):
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


class WishListQueryset(QuerySet):
    def get_table_joined(self):
        return self.values(
            "current_mos",
            "buy_mos",
            "company__tidm",
            "company__company_name",
            "decision__value",
        )


class PortfolioQueryset(QuerySet):
    def get_table_joined(self):
        return self.values(
            "num_shares",
            "current_stock_price",
            "company",
            "company__tidm",
            "company__company_name",
        )


def cost_pie_chart(portfolio_df):
    fig = px.pie(portfolio_df, values='price', names='company__company_name')
    plot_div = plot(fig, output_type='div')

    return plot_div


def get_chart_2(portfolio_df):
    fig2 = px.bar(x=["a", "b", "c"], y=[1, 2, 3])
    plot_div2 = plot(fig2, output_type='div')

    return plot_div2
