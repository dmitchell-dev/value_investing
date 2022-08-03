import django_tables2 as tables

from financial_reports.models import FinancialReports


class FinancialReportsTable(tables.Table):
    class Meta:
        model = FinancialReports
        attrs = {"class": "table thead-light table-striped table-hover"}
        # fields = (...)
