import django_tables2 as tables
from django_tables2.utils import A


class NameTable(tables.Table):
    company_name = tables.LinkColumn('dashboard_company:dashboard_detail', args=[A("pk")])
    tidm = tables.Column()
    fees_paid = tables.Column()
    share_price_paid = tables.Column()
    latest_share_price = tables.Column()
    number_shares_held = tables.Column()
    latest_total_value = tables.Column()
    value_change = tables.Column()
    pct_value_change = tables.Column()
