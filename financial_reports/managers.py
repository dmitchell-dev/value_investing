from django.db.models import QuerySet


class FinancialReportsQueryset(QuerySet):
    def get_financial_data_joined_filtered(self, tidm):
        return self.values(
            "parameter__param_name",
            "parameter__report_section__report_section",
            "time_stamp",
            "value",
        ).filter(company__tidm=tidm)

        # session.query(FinancialObjects)
        # .join(Companies)
        # .join(Parameters)
        # .join(ReportSection)
        # .with_entities(
        #     Parameters.param_name,
        #     ReportSection.report_section,
        #     FinancialObjects.time_stamp,
        #     FinancialObjects.value,
        # )
        # .filter(Companies.tidm == tidm)
