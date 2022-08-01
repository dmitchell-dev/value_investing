import django_tables2 as tables

from .models import DcfVariables


class DCFTable(tables.Table):
    class Meta:
        model = DcfVariables
        attrs = {"class": "table thead-light table-striped table-hover"}
        # fields = (...)
