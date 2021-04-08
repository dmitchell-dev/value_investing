from django.db import models
from django.urls import reverse


class DashboardCompany(models.Model):
    tidm = models.CharField(max_length=255, null=True)
    company_name = models.CharField(max_length=255, null=True)
    company_summary = models.TextField()
    share_listing = models.CharField(max_length=255, null=True)
    company_type = models.CharField(max_length=255, null=True)
    industry_name = models.CharField(max_length=255, null=True)
    turnover = models.FloatField()
    earnings = models.FloatField()
    dividends = models.FloatField()
    total_borrowing = models.FloatField()
    shareholder_equity = models.FloatField()
    capital_expenditure = models.FloatField()
    depreciation_amortisation = models.FloatField()
    acquisitions = models.FloatField()
    avg_shares = models.FloatField()
    share_price = models.FloatField()
    debt_to_equity = models.FloatField()
    current_ratio = models.FloatField()
    return_on_equity = models.FloatField()
    equity_per_share = models.FloatField()
    price_to_earnings = models.FloatField()
    price_to_equity = models.FloatField()
    annual_return = models.FloatField()
    fcf_growth_rate = models.FloatField()
    dividend_payment = models.CharField(max_length=10, null=True)
    dividend_cover = models.FloatField()
    revenue_growth = models.CharField(max_length=10, null=True)
    eps_growth = models.CharField(max_length=10, null=True)
    dividend_growth = models.CharField(max_length=10, null=True)
    growth_quality = models.FloatField()
    revenue_rowth_10 = models.FloatField()
    earnings_growth_10 = models.FloatField()
    dividend_growth_10 = models.FloatField()
    overall_growth_10 = models.FloatField()
    growth_rate_10 = models.FloatField()
    capital_employed = models.FloatField()
    roce = models.FloatField()
    median_roce_10 = models.FloatField()
    debt_ratio = models.FloatField()
    pe_10 = models.FloatField()
    dp_10 = models.FloatField()
    growth_rate_10_rank_value = models.FloatField()
    growth_quality_rank_value = models.FloatField()
    median_roce_10_rank_value = models.FloatField()
    pe_10_rank_value = models.FloatField()
    dp_10_rank_value = models.FloatField()
    growth_rate_10_rank = models.IntegerField()
    growth_quality_rank = models.IntegerField()
    median_roce_10_rank = models.IntegerField()
    pe_10_rank = models.IntegerField()
    dp_10_rank = models.IntegerField()
    defensive_rank = models.IntegerField()
    dcf_intrinsic_value = models.FloatField()
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
