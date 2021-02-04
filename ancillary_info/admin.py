from django.contrib import admin

from .models import (Markets,
                     CompanyType,
                     IndustryRisk,
                     ReportType,
                     Industries,
                     ReportSection,
                     Parameters,
                     CalcVariables,
                     Companies,
                     )


class MarketsAdmin(admin.ModelAdmin):
    fields = ['share_listing']


class CompanyTypeAdmin(admin.ModelAdmin):
    fields = ['company_type']


class IndustryRiskAdmin(admin.ModelAdmin):
    fields = ['industry_type']


class ReportTypeAdmin(admin.ModelAdmin):
    fields = ['report_name']


class IndustriesAdmin(admin.ModelAdmin):
    fields = ['industry_risk', 'industry_name']
    list_display = ('industry_name', 'industry_risk',)


class ReportSectionAdmin(admin.ModelAdmin):
    fields = ['report_type', 'report_section', 'report_section_last']
    list_display = ('report_section', 'report_type', 'report_section_last',)


class ParametersAdmin(admin.ModelAdmin):
    fields = ['report_section', 'param_name', 'limit_logic', 'limit_value', 'param_description']
    list_display = ('param_name', 'report_section', 'limit_logic', 'limit_value', 'param_description',)


class CalcVariablesAdmin(admin.ModelAdmin):
    fields = ['parameter', 'value']


class CompaniesAdmin(admin.ModelAdmin):
    fields = ['comp_type', 'industry', 'market', 'tidm', 'company_name', 'company_summary']
    list_display = ('company_name', 'tidm', 'comp_type', 'industry', 'market', 'company_summary',)


admin.site.register(Markets, MarketsAdmin)
admin.site.register(CompanyType, CompanyTypeAdmin)
admin.site.register(IndustryRisk, IndustryRiskAdmin)
admin.site.register(ReportType, ReportTypeAdmin)
admin.site.register(Industries, IndustriesAdmin)
admin.site.register(ReportSection, ReportSectionAdmin)
admin.site.register(Parameters, ParametersAdmin)
admin.site.register(CalcVariables, CalcVariablesAdmin)
admin.site.register(Companies, CompaniesAdmin)
