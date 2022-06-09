from django.db.models import QuerySet


class FinancialReportsQueryset(QuerySet):
    def get_financial_data_joined_filtered(self, tidm):
        return self.values(
            "parameter__param_name",
            "time_stamp",
            "value",
        ).filter(company__tidm=tidm)

    def get_financial_data_joined(self):
        return self.values(
            "company__tidm",
            "parameter__param_name",
            "time_stamp",
            "value",
        )

    def get_latest_date(self, tidm):
        if self.filter(company__tidm=tidm):
            return self.filter(company__tidm=tidm).latest("time_stamp")
        else:
            return []
