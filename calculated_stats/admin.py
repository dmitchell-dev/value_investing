from django.contrib import admin
from .models import CalculatedStats, DcfVariables


class CalculatedStatsAdmin(admin.ModelAdmin):
    fields = ["company_name", "param_name", "value", "timestamp"]


class DcfVariablesAdmin(admin.ModelAdmin):
    fields = ["company_name", "param_name", "value"]


admin.site.register(CalculatedStats, CalculatedStatsAdmin)
admin.site.register(DcfVariables, DcfVariablesAdmin)
