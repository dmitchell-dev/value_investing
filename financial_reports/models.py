from django.db import models
from ancillary_info.models import Companies, Parameters


class FinancialReports(models.Model):
    company_id = models.ForeignKey(Companies, on_delete=models.CASCADE)
    parameter_id = models.ForeignKey(Parameters, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField()
    value = models.FloatField()

    class Meta:
        db_table = "reporting_data"
        verbose_name_plural = "Financial Reports"

    def __str__(self):
        return self.company_name
