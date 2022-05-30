from django.db.models import QuerySet


class SharePricesQueryset(QuerySet):
    def get_share_joined(self):
        return self.values(
            "id",
            "time_stamp",
            "value",
            "volume",
            "company__company_name",
            "company__tidm",
        )

    def get_share_joined_filtered(self, tidm):
        return self.values(
            "id",
            "time_stamp",
            "value",
            "volume",
            "company__company_name",
            "company__tidm",
        ).filter(company__tidm=tidm)

    def get_latest_date(self, tidm):
        return self.filter(company__tidm=tidm).latest("time_stamp")
