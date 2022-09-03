from django.db.models import QuerySet


class DashboardCompanyQueryset(QuerySet):
    def get_tidm_from_id(self, val):
        tidm = self.values("tidm",).filter(id=val)[
            0
        ]["tidm"]

        return tidm

    def get_dash_joined(self):
        return self.values(
            "id",
            "tidm",
            "company_name",
        )

    def get_table_joined(self):
        return self.values(
            "id",
            "tidm",
            "latest_share_price",
        )
