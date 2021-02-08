from django.db import models
from .managers import (
    CompaniesQueryset,
    ParametersQueryset,
    CalcVariablesQueryset,
)


class Markets(models.Model):
    share_listing = models.CharField(max_length=255)

    class Meta:
        db_table = "markets"
        verbose_name_plural = "Markets"

    def __str__(self):
        return self.share_listing


class CompanyType(models.Model):
    company_type = models.CharField(max_length=255)

    class Meta:
        db_table = "company_type"
        verbose_name_plural = "Company Types"

    def __str__(self):
        return self.company_type


class IndustryRisk(models.Model):
    industry_type = models.CharField(max_length=255)

    class Meta:
        db_table = "industry_risk"
        verbose_name_plural = "Industry Risks"

    def __str__(self):
        return self.industry_type


class ReportType(models.Model):
    report_name = models.CharField(max_length=255)

    class Meta:
        db_table = "report_type"
        verbose_name_plural = "Report Types"

    def __str__(self):
        return self.report_name


class Industries(models.Model):
    industry_risk = models.ForeignKey(IndustryRisk, on_delete=models.CASCADE)
    industry_name = models.CharField(max_length=255)

    class Meta:
        db_table = "industries"
        verbose_name_plural = "Industries"

    def __str__(self):
        return self.industry_name


class ReportSection(models.Model):
    report_type = models.ForeignKey(ReportType, on_delete=models.CASCADE)
    report_section = models.CharField(max_length=255)
    report_section_last = models.CharField(max_length=255)

    class Meta:
        db_table = "report_section"
        verbose_name_plural = "Report Sections"

    def __str__(self):
        return self.report_section


class Parameters(models.Model):
    report_section = models.ForeignKey(ReportSection, on_delete=models.CASCADE)
    param_name = models.CharField(max_length=255)
    limit_logic = models.CharField(max_length=255)
    limit_value = models.CharField(max_length=255)
    param_description = models.CharField(max_length=255)

    objects = ParametersQueryset.as_manager()

    class Meta:
        db_table = "parameters"
        verbose_name_plural = "Parameters"

    def __str__(self):
        return self.param_name


class CalcVariables(models.Model):
    parameter = models.ForeignKey(Parameters, on_delete=models.CASCADE)
    value = models.FloatField()

    objects = CalcVariablesQueryset.as_manager()

    class Meta:
        db_table = "calc_variables"
        verbose_name_plural = "Calculation Variables"

    def __str__(self):
        return self.parameter.param_name


class Companies(models.Model):
    comp_type = models.ForeignKey(CompanyType, on_delete=models.CASCADE)
    industry = models.ForeignKey(Industries, on_delete=models.CASCADE)
    market = models.ForeignKey(Markets, on_delete=models.CASCADE)
    tidm = models.CharField(max_length=10)
    company_name = models.CharField(max_length=255)
    company_summary = models.TextField()

    objects = CompaniesQueryset.as_manager()

    class Meta:
        db_table = "companies"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.company_name
