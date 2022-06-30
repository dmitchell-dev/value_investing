from django.db.models import QuerySet


class DashboardCompanyQueryset(QuerySet):
    def get_tidm_from_id(self, val):
        tidm = self.values(
            "tidm",
        ).filter(id=val)[0]['tidm']

        return tidm
