from django.db import models
from django.urls import reverse


class DashboardCompany(models.Model):
    tidm = models.CharField(max_length=255, null=True)
    company_name = models.CharField(max_length=255, null=True)
    company_summary = models.TextField()
    share_listing = models.CharField(max_length=255, null=True)
    company_type = models.CharField(max_length=255, null=True)
    industry_name = models.CharField(max_length=255, null=True)
    revenue = models.FloatField()
    earnings = models.FloatField()
    dividends = models.FloatField()
    capital_expenditure = models.FloatField()
    net_income = models.FloatField()
    total_equity = models.FloatField()
    share_price = models.FloatField()
    debt_to_equity = models.FloatField()
    current_ratio = models.FloatField()
    return_on_equity = models.FloatField()
    equity_per_share = models.FloatField()
    price_to_earnings = models.FloatField()
    price_to_equity = models.FloatField()
    earnings_yield_return = models.FloatField()
    fcf = models.FloatField()
    dividend_payment = models.CharField(max_length=10, null=True)
    dividend_cover = models.FloatField()
    capital_employed = models.FloatField()
    roce = models.FloatField()
    dcf_intrinsic_value = models.FloatField()
    margin_safety = models.FloatField()
    estimated_growth_rate = models.FloatField()
    estimated_discount_rate = models.FloatField()
    estimated_long_term_growth_rate = models.FloatField()

    # objects = CalculatedStatsQueryset.as_manager()

    class Meta:
        db_table = "dashboard_company"
        verbose_name_plural = "Dashboard Companies"

    def __str__(self):
        return self.company_name

    def get_absolute_url(self):
        return reverse("dashboard_company:dashboard_detail", args=[str(self.id)])
