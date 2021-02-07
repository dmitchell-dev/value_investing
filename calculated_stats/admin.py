from django.contrib import admin
from .models import CalculatedStats


class CalculatedStatsAdmin(admin.ModelAdmin):
    fields = ["company_name", "param_name", "value", "timestamp"]


admin.site.register(CalculatedStats, CalculatedStatsAdmin)
