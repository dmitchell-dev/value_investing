import django_tables2 as tables

from datetime import datetime
import pytz
from dateutil import relativedelta

from django_tables2.utils import A

from .models import DashboardCompany


class DashboardCompanyTable(tables.Table):
    company_name = tables.LinkColumn(
        "dashboard_company:dashboard_detail", args=[A("pk")]
    )

    def __init__(self, *args, **kwargs):
        super(DashboardCompanyTable, self).__init__(*args, **kwargs)

    def render_revenue(self, value, record):
        return f"{record.currency_symbol}{value:.2f}"

    def render_fcf(self, value, record):
        return f"{record.currency_symbol}{value:.2f}"

    def render_share_price(self, value, record):
        return f"{record.currency_symbol}{value:.2f}"

    def render_dcf_intrinsic_value(self, value, record):
        return f"{record.currency_symbol}{value:.2f}"

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
            "latest_financial_date",
            "latest_share_price_date",
            "decision_type",
        )
