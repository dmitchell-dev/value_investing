import django_tables2 as tables

from calculated_stats.models import DcfVariables


class DCFTable(tables.Table):
    class Meta:
        model = DcfVariables
