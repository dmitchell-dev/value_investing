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
    CompSource,
    Companies,
    DecisionType,
    DcfVariables,
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
    fields = [
        "symbol",
        "value",
    ]


class CountriesAdmin(admin.ModelAdmin):
    fields = ["value"]


class ReportTypeAdmin(admin.ModelAdmin):
    fields = ["value"]


class DatasourceAdmin(admin.ModelAdmin):
    fields = ["source_name"]


class CompSourceAdmin(admin.ModelAdmin):
    fields = ["value"]


class DecisionTypeAdmin(admin.ModelAdmin):
    fields = ["value"]


class DcfVariablesAdmin(admin.ModelAdmin):
    fields = [
        "est_growth_rate",
        "est_disc_rate",
        "est_ltg_rate",
    ]


class ParamsApiAdmin(admin.ModelAdmin):
    fields = [
        "param_name_api",
        "datasource_id",
        "param_id",
    ]


class ParamsAdmin(admin.ModelAdmin):
    fields = [
        "param_name",
        "param_name_col",
        "report_type",
        "limit_logic",
        "limit_value",
        "data_type",
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
        "company_source",
        "company_name",
        "company_summary",
    ]
    list_display = (
        "company_name",
        "tidm",
        "comp_type",
        "industry",
        "exchange",
        "company_source",
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
admin.site.register(CompSource, CompSourceAdmin)
admin.site.register(Companies, CompaniesAdmin)
admin.site.register(DecisionType, DecisionTypeAdmin)
admin.site.register(DcfVariables, DcfVariablesAdmin)
