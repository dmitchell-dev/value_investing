import django_tables2 as tables

from django_tables2.utils import A

from .models import DashboardCompany


class DashboardCompanyTable(tables.Table):
    company_name = tables.LinkColumn(
        "dashboard_company:dashboard_detail", args=[A("pk")]
    )

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
