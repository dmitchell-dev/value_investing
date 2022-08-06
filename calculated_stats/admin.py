from django.contrib import admin
from .models import CalculatedStats


class CalculatedStatsAdmin(admin.ModelAdmin):
    fields = ["company", "parameter", "value", "time_stamp"]


admin.site.register(CalculatedStats, CalculatedStatsAdmin)
