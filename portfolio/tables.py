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

    class Meta:
        model = WishList
        attrs = {"class": "table thead-light table-striped table-hover"}
        fields = (
            "company__company_name",
            "decision__value",
            "reporting_stock_price",
            "reporting_mos",
            "buy_mos",
            "created_at",
            "updated_at",
        )
