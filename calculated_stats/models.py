from django.db import models
from ancillary_info.models import Companies, Params
from .managers import CalculatedStatsQueryset


class CalculatedStats(models.Model):
    company = models.ForeignKey(Companies, on_delete=models.CASCADE)
    parameter = models.ForeignKey(Params, on_delete=models.CASCADE)
    time_stamp = models.DateField()
    value = models.CharField(max_length=255, null=True)

    objects = CalculatedStatsQueryset.as_manager()

    class Meta:
        db_table = "calculated_data"
        verbose_name_plural = "Calculated Data"

    def __str__(self):
        return f"{self.company} - {self.parameter} - {self.time_stamp}"
