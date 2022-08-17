from django.db import models
from .managers import (
    CompaniesQueryset,
    ParamsQueryset,
    ParamsApiQueryset,
    DcfVariablesQueryset,
)
from django.urls import reverse


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
    symbol = models.CharField(max_length=255)
    value = models.FloatField()

    class Meta:
        db_table = "currencies"
        verbose_name_plural = "Currencies"

    def __str__(self):
        return self.symbol


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


class DecisionType(models.Model):
    value = models.CharField(max_length=255)

    class Meta:
        db_table = "decision_type"
        verbose_name_plural = "Decision Types"

    def __str__(self):
        return self.value


class ParamsApi(models.Model):
    datasource = models.ForeignKey(Datasource, on_delete=models.CASCADE)
    param = models.ForeignKey(Params, on_delete=models.CASCADE)
    param_name_api = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    wish_list = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CompaniesQueryset.as_manager()

    class Meta:
        db_table = "companies"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.company_name

    def get_absolute_url(self):
        return reverse("ancillary:company_detail", kwargs={"pk": self.pk})


class DcfVariables(models.Model):
    company = models.ForeignKey(Companies, on_delete=models.CASCADE)
    est_growth_rate = models.FloatField()
    est_disc_rate = models.FloatField()
    est_ltg_rate = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = DcfVariablesQueryset.as_manager()

    class Meta:
        db_table = "dcf_variables"
        verbose_name_plural = "DCF Variables"

    def __str__(self):
        return f"{self.company}"
