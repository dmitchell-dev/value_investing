from django.db import models
from django.urls import reverse

from ancillary_info.models import Companies

from .managers import DashboardCompanyQueryset


class DashboardCompany(models.Model):
    company = models.ForeignKey(Companies, on_delete=models.CASCADE)
    tidm = models.CharField(max_length=255, null=True)
    company_name = models.CharField(max_length=255, null=True)
    company_summary = models.TextField()
    share_listing = models.CharField(max_length=255, null=True)
    company_type = models.CharField(max_length=255, null=True)
    industry_name = models.CharField(max_length=255, null=True)
    revenue = models.FloatField(null=True)
    earnings = models.FloatField(null=True)
    dividends = models.FloatField(null=True)
    capital_expenditure = models.FloatField(null=True)
    net_income = models.FloatField(null=True)
    total_equity = models.FloatField(null=True)
    share_price = models.FloatField(null=True)
    debt_to_equity = models.FloatField(null=True)
    current_ratio = models.FloatField(null=True)
    return_on_equity = models.FloatField(null=True)
    equity_per_share = models.FloatField(null=True)
    price_to_earnings = models.FloatField(null=True)
    price_to_equity = models.FloatField(null=True)
    earnings_yield = models.FloatField(null=True)
    annual_yield_return = models.FloatField(null=True)
    fcf = models.FloatField(null=True)
    dividend_cover = models.FloatField(null=True)
    capital_employed = models.FloatField(null=True)
    roce = models.FloatField(null=True)
    dcf_intrinsic_value = models.FloatField(null=True)
    margin_safety = models.FloatField(null=True)
    latest_margin_of_safety = models.FloatField(null=True)
    estimated_growth_rate = models.FloatField(null=True)
    estimated_discount_rate = models.FloatField(null=True)
    estimated_long_term_growth_rate = models.FloatField(null=True)
    pick_source = models.CharField(max_length=255)
    exchange_country = models.CharField(max_length=255)
    currency_symbol = models.CharField(max_length=5)
    latest_financial_date = models.DateTimeField(null=True)
    latest_share_price_date = models.DateTimeField(null=True)
    latest_share_price = models.FloatField(null=True)
    market_cap = models.FloatField(null=True)

    objects = DashboardCompanyQueryset.as_manager()

    class Meta:
        db_table = "dashboard_company"
        verbose_name_plural = "Dashboard Companies"

    def __str__(self):
        return self.company_name

    def get_absolute_url(self):
        return reverse("dashboard_company:dashboard_detail", args=[str(self.id)])
