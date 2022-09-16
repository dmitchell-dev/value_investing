from django.db.models import QuerySet


class DashboardCompanyQueryset(QuerySet):
    def get_tidm_from_id(self, val):
        tidm = self.values("tidm",).filter(id=val)[
            0
        ]["tidm"]

        return tidm

    def get_compid_from_dashid(self, val):
        comp_id = self.values("company_id",).filter(id=val)[
            0
        ]["company_id"]

        return comp_id

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
            "company_name",
            "company_id",
            "latest_share_price",
        )
