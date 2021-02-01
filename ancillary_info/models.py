from django.db import models


class Markets(models.Model):
    share_listing = models.CharField(max_length=255)

    class Meta:
        db_table = 'markets'


class CompanyType(models.Model):
    company_type = models.CharField(max_length=255)

    class Meta:
        db_table = 'company_type'


class IndustryRisk(models.Model):
    industry_type = models.CharField(max_length=255)

    class Meta:
        db_table = 'industry_risk'


class ReportType(models.Model):
    report_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'report_type'


class Industries(models.Model):
    industry_risk = models.ForeignKey(
        IndustryRisk,
        on_delete=models.CASCADE
        )
    industry_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'industries'


class ReportSection(models.Model):
    report_type = models.ForeignKey(
        ReportType,
        on_delete=models.CASCADE
        )
    report_section = models.CharField(max_length=255)
    report_section_last = models.CharField(max_length=255)

    class Meta:
        db_table = 'report_section'


class Parameters(models.Model):
    report_section = models.ForeignKey(
        ReportSection,
        on_delete=models.CASCADE
        )
    param_name = models.CharField(max_length=255)
    limit_logic = models.CharField(max_length=255)
    limit_value = models.CharField(max_length=255)
    param_description = models.CharField(max_length=255)

    class Meta:
        db_table = 'parameters'


class CalcVariables(models.Model):
    parameter = models.ForeignKey(
        Parameters,
        on_delete=models.CASCADE
        )
    value = models.FloatField()

    class Meta:
        db_table = 'calc_variables'


class Companies(models.Model):
    comp_type = models.ForeignKey(
        CompanyType,
        on_delete=models.CASCADE
        )
    industry = models.ForeignKey(
        Industries,
        on_delete=models.CASCADE
        )
    market = models.ForeignKey(
        Markets,
        on_delete=models.CASCADE
        )
    tidm = models.CharField(max_length=10)
    company_name = models.CharField(max_length=255)
    company_summary = models.TextField()

    class Meta:
        db_table = 'companies'
