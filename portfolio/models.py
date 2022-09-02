from django.db import models
from django.urls import reverse
from ancillary_info.models import Companies, DecisionType
from .managers import (
    TransactionsQueryset,
    WishListQueryset,
    PortfolioQueryset,
)


class Transactions(models.Model):
    company = models.ForeignKey(Companies, on_delete=models.CASCADE)
    decision = models.ForeignKey(DecisionType, on_delete=models.CASCADE)
    date_dealt = models.DateField(blank=False)
    date_settled = models.DateField(blank=False)
    reference = models.CharField(max_length=255)
    num_stock = models.IntegerField()
    price = models.FloatField()
    fees = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TransactionsQueryset.as_manager()

    class Meta:
        db_table = "transactions"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.company} - {self.decision} - {self.created_at}"

    def get_absolute_url(self):
        return reverse("portfolio:transaction_detail", kwargs={"pk": self.pk})


class WishList(models.Model):
    company = models.OneToOneField(Companies, on_delete=models.CASCADE, primary_key=True)
    reporting_stock_price = models.FloatField()
    current_stock_price = models.FloatField()
    reporting_mos = models.FloatField()
    current_mos = models.FloatField()
    buy_mos = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = WishListQueryset.as_manager()

    class Meta:
        db_table = "wish_list"
        verbose_name_plural = "Wish List"

    def __str__(self):
        return f"{self.company} - {self.decision} - {self.buy_mos}"

    def get_absolute_url(self):
        return reverse("dashboard_company:dashboard_detail", kwargs={"pk": self.pk})


class Portfolio(models.Model):
    company = models.ForeignKey(Companies, on_delete=models.CASCADE)
    num_shares = models.IntegerField()
    current_stock_price = models.FloatField()
    cash_holding = models.FloatField()

    objects = PortfolioQueryset.as_manager()

    class Meta:
        db_table = "portfolio"
        verbose_name_plural = "Portfolio"

    def __str__(self):
        return f"{self.company} - {self.num_shares} - {self.current_stock_price}"
