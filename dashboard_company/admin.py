from django.contrib import admin
from .models import DashboardCompany


class DashboardCompanyAdmin(admin.ModelAdmin):
    fields = [
        "company_name",
        "share_listing",
        "company_type",
        "industry_name",
        "industry_type",
    ]


admin.site.register(DashboardCompany, DashboardCompanyAdmin)
