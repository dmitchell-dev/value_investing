from django.contrib import admin
from .models import FinancialReports


class FinancialReportsAdmin(admin.ModelAdmin):
    fields = ["company", "parameter", "value", "time_stamp"]


admin.site.register(FinancialReports, FinancialReportsAdmin)
