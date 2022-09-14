import django_tables2 as tables

from django_tables2.utils import A

from .models import DashboardCompany


class DashboardCompanyTable(tables.Table):
    company_name = tables.LinkColumn(
        "dashboard_company:dashboard_detail", args=[A("pk")]
    )

    def __init__(self, *args, **kwargs):
        super(DashboardCompanyTable, self).__init__(*args, **kwargs)

    def render_revenue(self, value, record):
        print(record.currency_symbol)
        return f"{record.currency_symbol}{value:.2f}"

    def render_fcf(self, value, record):
        return f"{record.currency_symbol}{value:.2f}"

    def render_share_price(self, value, record):
        return f"{record.currency_symbol}{value:.2f}"

    def render_dcf_intrinsic_value(self, value, record):
        return f"{record.currency_symbol}{value:.2f}"

    class Meta:
        model = DashboardCompany
        attrs = {"class": "table thead-light table-striped table-hover"}
        fields = (
            "company_name",
            "revenue",
            "fcf",
            "share_price",
            "dcf_intrinsic_value",
            "margin_safety",
            "latest_margin_of_safety",
        )
