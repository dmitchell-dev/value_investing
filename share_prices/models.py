from django.db import models
from ancillary_info.models import Companies
from .managers import SharePricesQueryset, ShareSplitsQueryset


class SharePrices(models.Model):
    company = models.ForeignKey(Companies, on_delete=models.CASCADE)
    time_stamp = models.DateField()
    value = models.FloatField(null=True)
    volume = models.BigIntegerField(null=True)

    objects = SharePricesQueryset.as_manager()

    class Meta:
        db_table = "share_price"
        verbose_name_plural = "Share Prices"

    def __str__(self):
        return self.company


class ShareSplits(models.Model):
    company = models.ForeignKey(Companies, on_delete=models.CASCADE)
    time_stamp = models.DateField()
    value = models.FloatField(null=True)
    volume = models.BigIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ShareSplitsQueryset.as_manager()

    class Meta:
        db_table = "share_split"
        verbose_name_plural = "Share Splits"

    def __str__(self):
        return self.company
