from django.contrib import admin
from .models import FinancialReports


class FinancialReportsAdmin(admin.ModelAdmin):
    fields = ["company_name", "param_name", "value", "timestamp"]


admin.site.register(FinancialReports, FinancialReportsAdmin)
