from django.db import models
from .managers import (
    CompaniesQueryset,
    ParamsQueryset,
)


class Exchanges(models.Model):
    value = models.CharField(max_length=255)

    class Meta:
        db_table = "exchanges"
        verbose_name_plural = "Exchanges"

    def __str__(self):
        return self.share_listing


class CompanyType(models.Model):
    value = models.CharField(max_length=255)

    class Meta:
        db_table = "company_type"
        verbose_name_plural = "Company Types"

    def __str__(self):
        return self.company_type


class Industries(models.Model):
    value = models.CharField(max_length=255)

    class Meta:
        db_table = "industries"
        verbose_name_plural = "Industries"

    def __str__(self):
        return self.industry_name


class Sectors(models.Model):
    value = models.CharField(max_length=255)

    class Meta:
        db_table = "sectors"
        verbose_name_plural = "Sectors"

    def __str__(self):
        return self.industry_type


class Currencies(models.Model):
    value = models.CharField(max_length=255)

    class Meta:
        db_table = "currencies"
        verbose_name_plural = "Currencies"

    def __str__(self):
        return self.industry_type


class Countries(models.Model):
    value = models.CharField(max_length=255)

    class Meta:
        db_table = "countries"
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.industry_type


class ReportType(models.Model):
    value = models.CharField(max_length=255)

    class Meta:
        db_table = "report_type"
        verbose_name_plural = "Report Types"

    def __str__(self):
        return self.report_name


class Params(models.Model):
    report_type = models.ForeignKey(ReportType, on_delete=models.CASCADE)
    param_name = models.CharField(max_length=255)
    param_name_col = models.CharField(max_length=255)
    limit_logic = models.CharField(max_length=255)
    limit_value = models.CharField(max_length=255)
    data_type = models.CharField(max_length=255)
    param_description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ParamsQueryset.as_manager()

    class Meta:
        db_table = "params"
        verbose_name_plural = "Parameters"

    def __str__(self):
        return self.param_name


class Datasource(models.Model):
    source_name = models.CharField(max_length=255)

    class Meta:
        db_table = "datasource"
        verbose_name_plural = "Datasources"

    def __str__(self):
        return self.param_name


class ParamsApi(models.Model):
    datasource = models.ForeignKey(Datasource, on_delete=models.CASCADE)
    param = models.ForeignKey(Params, on_delete=models.CASCADE)
    param_name_api = models.CharField(max_length=255)

    objects = ParamsQueryset.as_manager()

    class Meta:
        db_table = "params_api"
        verbose_name_plural = "API Parameters"

    def __str__(self):
        return self.param_name


class Companies(models.Model):
    comp_type = models.ForeignKey(CompanyType, on_delete=models.CASCADE)
    industry = models.ForeignKey(Industries, on_delete=models.CASCADE)
    exchange = models.ForeignKey(Exchanges, on_delete=models.CASCADE)
    tidm = models.CharField(max_length=10)
    company_name = models.CharField(max_length=255)
    company_summary = models.TextField()

    objects = CompaniesQueryset.as_manager()

    class Meta:
        db_table = "companies"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.company_name
