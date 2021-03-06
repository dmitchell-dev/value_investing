from django.contrib import admin
from .models import SharePrices


class SharePricesAdmin(admin.ModelAdmin):
    fields = ["company", "time_stamp", "value", "volume", "adjustment"]


admin.site.register(SharePrices, SharePricesAdmin)
