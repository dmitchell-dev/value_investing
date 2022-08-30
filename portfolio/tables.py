import django_tables2 as tables
from django_tables2.utils import A

from .models import WishList


class NameTable(tables.Table):
    company_name = tables.LinkColumn(
        "dashboard_company:dashboard_detail", args=[A("pk")]
    )
    tidm = tables.Column()
    fees_paid = tables.Column()
    share_price_paid = tables.Column()
    latest_share_price = tables.Column()
    number_shares_held = tables.Column()
    total_cost = tables.Column()
    latest_total_value = tables.Column()
    value_change = tables.Column()
    pct_value_change = tables.Column()


class WishListTable(tables.Table):
    company__company_name = tables.LinkColumn("portfolio:wishlist_detail", args=[A("pk")])

    def __init__(self, *args, **kwargs):
        super(WishListTable, self).__init__(*args, **kwargs)
        self.maxpts = 0.5

    # render_foo example method
    def render_current_mos(self, value, column):
        if value < self.maxpts and value >= 0:
            column.attrs = {'td': {'bgcolor': '#90EE90'}}  # Light Green
        elif value < 0:
            column.attrs = {'td': {'bgcolor': '#FFCCCB'}}  # Light Red
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
        )
