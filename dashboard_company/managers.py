from django.db.models import QuerySet


class DashboardCompanyQueryset(QuerySet):
    def get_tidm_from_id(self, val):
        tidm = self.values("tidm",).filter(company_id=val)[
            0
        ]["tidm"]

        return tidm

    def get_dash_joined(self):
        return self.values(
            "company_id",
            "tidm",
            "company_name",
        )

    def get_table_joined(self):
        return self.values(
            "company_id",
            "tidm",
            "company_name",
            "latest_share_price",
        )
