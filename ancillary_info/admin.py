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
    fields = ['industry_risk_id', 'industry_name']


class ReportSectionAdmin(admin.ModelAdmin):
    fields = ['report_type_id', 'report_section', 'report_section_last']


class ParametersAdmin(admin.ModelAdmin):
    fields = ['report_section_id', 'param_name', 'limit_logic', 'limit_value', 'param_description']


class CalcVariablesAdmin(admin.ModelAdmin):
    fields = ['parameter_id', 'value']


class CompaniesAdmin(admin.ModelAdmin):
    fields = ['comp_type_id', 'industry_id', 'market_id', 'tidm', 'company_name', 'company_summary']


admin.site.register(Markets, MarketsAdmin)
admin.site.register(CompanyType, CompanyTypeAdmin)
admin.site.register(IndustryRisk, IndustryRiskAdmin)
admin.site.register(ReportType, ReportTypeAdmin)
admin.site.register(Industries, IndustriesAdmin)
admin.site.register(ReportSection, ReportSectionAdmin)
admin.site.register(Parameters, ParametersAdmin)
admin.site.register(CalcVariables, CalcVariablesAdmin)
admin.site.register(Companies, CompaniesAdmin)
