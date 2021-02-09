from django.db import models
from ancillary_info.models import Companies
from .managers import SharePricesQueryset


class SharePrices(models.Model):
    company = models.ForeignKey(Companies, on_delete=models.CASCADE)
    time_stamp = models.DateField()
    value = models.FloatField(null=True)
    volume = models.IntegerField(null=True)
    adjustment = models.SmallIntegerField(null=True)

    objects = SharePricesQueryset.as_manager()

    class Meta:
        db_table = "share_price"
        verbose_name_plural = "Share Prices"

    def __str__(self):
        return self.company
