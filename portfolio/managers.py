from django.db.models import QuerySet


class InvestmentsQueryset(QuerySet):
    def get_table_joined(self):
        return self.values(
            "num_stock",
            "decision",
            "reference",
            "price",
            "fees",
            "created_at",
            "date_dealt",
            "date_settled",
            "company__tidm",
            "company__company_name",
            "company__industry",
            "company__sector",
            "company__exchange",
            "company__country",
            "company__currency",
            "decision__value",
        )


class WishListQueryset(QuerySet):
    def get_table_joined(self):
        return self.values(
            "current_mos",
            "buy_mos",
            "company__tidm",
            "company__company_name",
            "decision__value",
        )


class PortfolioQueryset(QuerySet):
    def get_table_joined(self):
        return self.values(
            "num_shares",
            "current_stock_price",
            "company__tidm",
            "company__company_name",
        )
