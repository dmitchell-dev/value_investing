from django.db import models
from ancillary_info.models import Companies, Params
from .managers import FinancialReportsQueryset


class FinancialReports(models.Model):
    company = models.ForeignKey(Companies, on_delete=models.CASCADE)
    parameter = models.ForeignKey(Params, on_delete=models.CASCADE)
    time_stamp = models.DateField()
    value = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = FinancialReportsQueryset.as_manager()

    class Meta:
        db_table = "reporting_data"
        verbose_name_plural = "Financial Reports"

    def __str__(self):
        return f"{self.company} - {self.parameter} - {self.time_stamp}"
