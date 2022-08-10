from django.db.models import QuerySet


class SharePricesQueryset(QuerySet):
    def get_share_joined(self):
        return self.values(
            "id",
            "time_stamp",
            "value",
            "value_adjusted",
            "volume",
            "company__company_name",
            "company__tidm",
        )

    def get_share_joined_filtered(self, tidm):
        return self.values(
            "id",
            "time_stamp",
            "value",
            "value_adjusted",
            "volume",
            "company__company_name",
            "company__tidm",
        ).filter(company__tidm=tidm)

    def get_share_filtered(self, tidm):
        return self.values(
            "id",
            "time_stamp",
            "value",
            "value_adjusted",
            "volume",
            "company",
        ).filter(company__tidm=tidm)

    def get_latest_date(self, tidm):
        if self.filter(company__tidm=tidm):
            return self.filter(company__tidm=tidm).latest("time_stamp")
        else:
            return []

    def get_latest_share_price(self, tidm):
        if self.filter(company__tidm=tidm):
            return self.filter(company__tidm=tidm).latest("value_adjusted")
        else:
            return []


class ShareSplitsQueryset(QuerySet):
    def get_share_joined(self):
        return self.values(
            "id",
            "time_stamp",
            "value",
            "created_at",
            "updated_at",
            "company__company_name",
            "company__tidm",
        )

    def get_share_joined_filtered(self, tidm):
        return self.values(
            "id",
            "time_stamp",
            "value",
            "created_at",
            "updated_at",
            "company__company_name",
            "company__tidm",
        ).filter(company__tidm=tidm)

    def get_share_filtered(self, tidm):
        return self.values(
            "id",
            "time_stamp",
            "value",
            "created_at",
            "updated_at",
            "company",
        ).filter(company__tidm=tidm)

    def get_latest_date(self, tidm):
        if self.filter(company__tidm=tidm):
            return self.filter(company__tidm=tidm).latest("time_stamp")
        else:
            return []
