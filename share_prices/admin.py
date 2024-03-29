from django.contrib import admin
from .models import SharePrices, ShareSplits


class SharePricesAdmin(admin.ModelAdmin):
    fields = ["company", "time_stamp", "value", "value_adjusted", "volume"]


class ShareSplitsAdmin(admin.ModelAdmin):
    fields = ["company", "time_stamp", "value"]


admin.site.register(SharePrices, SharePricesAdmin)
admin.site.register(ShareSplits, ShareSplitsAdmin)
