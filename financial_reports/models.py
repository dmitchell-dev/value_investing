from django.db import models
from ancillary_info.models import Companies, Parameters
from .managers import FinancialReportsQueryset


class FinancialReports(models.Model):
    company = models.ForeignKey(Companies, on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameters, on_delete=models.CASCADE)
    time_stamp = models.DateField()
    value = models.FloatField(null=True)

    objects = FinancialReportsQueryset.as_manager()

    class Meta:
        db_table = "reporting_data"
        verbose_name_plural = "Financial Reports"

    def __str__(self):
        return f"{self.company} - {self.parameter} - {self.time_stamp}"
