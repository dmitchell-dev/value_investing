import django_tables2 as tables
from django_tables2.utils import A

from datetime import datetime
import pytz
from dateutil import relativedelta

from .models import WishList


class NameTable(tables.Table):
    company__company_name = tables.LinkColumn(
        "dashboard_company:dashboard_detail", args=[A("company")],
        verbose_name="Company Name",

    )
    company__tidm = tables.Column(verbose_name="TIDM")
    latest_shares_num = tables.Column(verbose_name="Number Shares")
    initial_shares_cost = tables.Column(verbose_name="Initial Shares Cost")
    latest_shares_holding = tables.Column(verbose_name="Latest Shares Holding")
    share_value_change = tables.Column(verbose_name="Share Value Change")
    share_pct_change = tables.Column(verbose_name="Share % Change")
    income_from_selling = tables.Column(verbose_name="Selling Income")
    total_profit = tables.Column(verbose_name="Profit")

    def __init__(self, *args, **kwargs):
        super(NameTable, self).__init__(*args, **kwargs)

    def render_fees_total(self, value):
        return f"£{value:.2f}"

    def render_initial_shares_cost(self, value):
        return f"£{value:.2f}"

    def render_latest_shares_holding(self, value):
        return f"£{value:.2f}"

    def render_income_from_selling(self, value):
        return f"£{value:.2f}"

    def render_total_profit(self, value):
        return f"£{value:.2f}"

    def render_share_value_change(self, value):
        return f"£{value:.2f}"

    def render_share_pct_change(self, value):
        return f"{value:.1f}%"


class WishListTable(tables.Table):
    company__company_name = tables.LinkColumn("portfolio:wishlist_detail", args=[A("pk")])

    def __init__(self, *args, **kwargs):
        super(WishListTable, self).__init__(*args, **kwargs)
        self.maxpts = 0.5

    def render_reporting_stock_price(self, value):
        return f"£{value:.2f}"

    def render_current_stock_price(self, value):
        return f"£{value:.2f}"

    def render_latest_financial_date(self, value, record):
        delta = relativedelta.relativedelta(datetime.now(pytz.utc), record.latest_financial_date)
        if delta.years == 0:
            year_str = ""
        else:
            year_str = f"{delta.years} Years, "
        rtn_str = year_str + f"{delta.months} Months, {delta.days} Days"
        return rtn_str

    def render_latest_share_price_date(self, value, record):
        delta = relativedelta.relativedelta(datetime.now(pytz.utc), record.latest_share_price_date)
        if delta.years == 0:
            year_str = ""
        else:
            year_str = f"{delta.years} Years, "
        rtn_str = year_str + f"{delta.months} Months, {delta.days} Days"
        return rtn_str

    # render_foo example method
    def render_current_mos(self, value, column):
        if value < self.maxpts and value >= 0:
            column.attrs = {'td': {'class': 'table-success'}}  # Light Green
        elif value < 0:
            column.attrs = {'td': {'class': 'table-success'}}  # Light Red
        else:
            column.attrs = {'td': {}}
        return value

    class Meta:
        model = WishList
        attrs = {"class": "table thead-light table-striped table-hover"}
        fields = (
            "company__company_name",
            "reporting_stock_price",
            "current_stock_price",
            "reporting_mos",
            "current_mos",
            "buy_mos",
            "latest_financial_date",
            "latest_share_price_date",
        )
