from django.contrib import admin

from .models import (
    Exchanges,
    CompanyType,
    Sectors,
    ReportType,
    Industries,
    Currencies,
    Countries,
    Params,
    Companies,
)


class ExchangesAdmin(admin.ModelAdmin):
    fields = ["value"]


class CompanyTypeAdmin(admin.ModelAdmin):
    fields = ["value"]


class IndustriesAdmin(admin.ModelAdmin):
    fields = ["value"]


class SectorsAdmin(admin.ModelAdmin):
    fields = ["value"]


class CurrenciesAdmin(admin.ModelAdmin):
    fields = ["value"]


class CountriesAdmin(admin.ModelAdmin):
    fields = ["value"]


class ReportTypeAdmin(admin.ModelAdmin):
    fields = ["value"]


class ParamsAdmin(admin.ModelAdmin):
    fields = [
        "param_name",
        "limit_logic",
        "limit_value",
        "param_description",
    ]
    list_display = (
        "param_name",
        "limit_logic",
        "limit_value",
        "param_description",
    )


class CompaniesAdmin(admin.ModelAdmin):
    fields = [
        "comp_type",
        "industry",
        "exchange",
        "tidm",
        "company_name",
        "company_summary",
    ]
    list_display = (
        "company_name",
        "tidm",
        "comp_type",
        "industry",
        "exchange",
        "company_summary",
    )


admin.site.register(Exchanges, ExchangesAdmin)
admin.site.register(CompanyType, CompanyTypeAdmin)
admin.site.register(Sectors, SectorsAdmin)
admin.site.register(ReportType, ReportTypeAdmin)
admin.site.register(Industries, IndustriesAdmin)
admin.site.register(Currencies, CurrenciesAdmin)
admin.site.register(Countries, CountriesAdmin)
admin.site.register(Params, ParamsAdmin)
admin.site.register(Companies, CompaniesAdmin)
