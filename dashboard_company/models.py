from django.db import models
from django.urls import reverse

from.managers import DashboardCompanyQueryset


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
    earnings_yield = models.FloatField()
    annual_yield_return = models.FloatField()
    fcf = models.FloatField()
    dividend_cover = models.FloatField()
    capital_employed = models.FloatField()
    roce = models.FloatField()
    dcf_intrinsic_value = models.FloatField()
    margin_safety = models.FloatField()
    estimated_growth_rate = models.FloatField()
    estimated_discount_rate = models.FloatField()
    estimated_long_term_growth_rate = models.FloatField()
    pick_source = models.CharField(max_length=255)
    exchange_country = models.CharField(max_length=255)
    currency_symbol = models.CharField(max_length=5)
    latest_financial_date = models.DateTimeField()
    latest_share_price_date = models.DateTimeField()
    market_cap = models.FloatField()

    objects = DashboardCompanyQueryset.as_manager()

    class Meta:
        db_table = "dashboard_company"
        verbose_name_plural = "Dashboard Companies"

    def __str__(self):
        return self.company_name

    def get_absolute_url(self):
        return reverse("dashboard_company:dashboard_detail", args=[str(self.id)])
