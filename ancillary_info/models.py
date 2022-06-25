from django.db import models
from .managers import (
    CompaniesQueryset,
    ParamsQueryset,
    ParamsApiQueryset,
)


class Exchanges(models.Model):
    value = models.CharField(max_length=255)

    class Meta:
        db_table = "exchanges"
        verbose_name_plural = "Exchanges"

    def __str__(self):
        return self.value


class CompanyType(models.Model):
    value = models.CharField(max_length=255)

    class Meta:
        db_table = "company_type"
        verbose_name_plural = "Company Types"

    def __str__(self):
        return self.value


class Industries(models.Model):
    value = models.CharField(max_length=255)

    class Meta:
        db_table = "industries"
        verbose_name_plural = "Industries"

    def __str__(self):
        return self.value


class Sectors(models.Model):
    value = models.CharField(max_length=255)

    class Meta:
        db_table = "sectors"
        verbose_name_plural = "Sectors"

    def __str__(self):
        return self.value


class Currencies(models.Model):
    value = models.CharField(max_length=255)

    class Meta:
        db_table = "currencies"
        verbose_name_plural = "Currencies"

    def __str__(self):
        return self.value


class Countries(models.Model):
    value = models.CharField(max_length=255)

    class Meta:
        db_table = "countries"
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.value


class ReportType(models.Model):
    value = models.CharField(max_length=255)

    class Meta:
        db_table = "report_type"
        verbose_name_plural = "Report Types"

    def __str__(self):
        return self.value


class Params(models.Model):
    report_type = models.ForeignKey(ReportType, on_delete=models.CASCADE)
    param_name = models.CharField(max_length=255)
    param_name_col = models.CharField(max_length=255)
    limit_logic = models.CharField(max_length=255)
    limit_value = models.CharField(max_length=255)
    data_type = models.CharField(max_length=255)
    param_description = models.TextField()
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
        db_table = "datasources"
        verbose_name_plural = "Datasources"

    def __str__(self):
        return self.source_name


class CompSource(models.Model):
    value = models.CharField(max_length=255)

    class Meta:
        db_table = "comp_sources"
        verbose_name_plural = "Company Sources"

    def __str__(self):
        return self.value


class ParamsApi(models.Model):
    datasource = models.ForeignKey(Datasource, on_delete=models.CASCADE)
    param = models.ForeignKey(Params, on_delete=models.CASCADE)
    param_name_api = models.CharField(max_length=255)

    objects = ParamsApiQueryset.as_manager()

    class Meta:
        db_table = "params_api"
        verbose_name_plural = "API Parameters"

    def __str__(self):
        return self.param_name_api


class Companies(models.Model):
    comp_type = models.ForeignKey(CompanyType, on_delete=models.CASCADE)
    industry = models.ForeignKey(Industries, on_delete=models.CASCADE)
    exchange = models.ForeignKey(Exchanges, on_delete=models.CASCADE)
    sector = models.ForeignKey(Sectors, on_delete=models.CASCADE)
    country = models.ForeignKey(Countries, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currencies, on_delete=models.CASCADE)
    company_source = models.ForeignKey(CompSource, on_delete=models.CASCADE)
    tidm = models.CharField(max_length=10)
    company_name = models.CharField(max_length=255)
    company_summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CompaniesQueryset.as_manager()

    class Meta:
        db_table = "companies"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.company_name
