from django.db import models
from ancillary_info.models import Companies, Parameters


class CalculatedStats(models.Model):
    company = models.ForeignKey(Companies, on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameters, on_delete=models.CASCADE)
    time_stamp = models.DateField()
    value = models.FloatField(null=True)

    class Meta:
        db_table = "calculated_data"
        verbose_name_plural = "Calculated Data"

    def __str__(self):
        return f"{self.company} - {self.parameter} - {self.time_stamp}"
