import django_tables2 as tables
from django_tables2.utils import A

from .models import DcfVariables, Companies


class DCFTable(tables.Table):
    class Meta:
        model = DcfVariables
        attrs = {"class": "table thead-light table-striped table-hover"}


class CompaniesTable(tables.Table):
    company_name = tables.LinkColumn("ancillary:company_detail", args=[A("pk")])

    class Meta:
        model = Companies
        attrs = {"class": "table thead-light table-striped table-hover"}
        fields = (
            "company_name",
            "tidm",
            "comp_type",
            "industry",
            "exchange",
            "company_source",
            "wish_list",
        )
