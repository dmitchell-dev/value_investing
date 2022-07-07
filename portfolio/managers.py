from django.db.models import QuerySet


class InvestmentsQueryset(QuerySet):
    def get_table_joined_filtered(self, tidm):
        return self.values(
            "num_stock",
            "price",
            "fees",
            "created_at",
            "date_dealt",
            "company__tidm",
            "company__company_name",
            "decision__value",
        ).filter(company__tidm=tidm)


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
