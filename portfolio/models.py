from django.db import models
from django.urls import reverse
from ancillary_info.models import Companies, DecisionType
from .managers import (
    TransactionsQueryset,
    CashQueryset,
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
    num_stock_balance = models.IntegerField()
    price = models.FloatField()
    fees = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TransactionsQueryset.as_manager()

    class Meta:
        db_table = "transactions"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.company} - {self.decision} - {self.num_stock} - {self.date_dealt}"

    def get_absolute_url(self):
        return reverse("portfolio:transaction_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        current_num_stock_balance = Transactions.objects.filter(company_id=self.company_id).latest('date_dealt').num_stock_balance

        # Increase or decrease depending on type
        if self.decision.value == 'Sold':
            self.num_stock_balance = current_num_stock_balance - self.num_stock
        elif self.decision.value == 'Bought':
            self.num_stock_balance = current_num_stock_balance + self.num_stock
        else:
            pass

        super(Transactions, self).save(*args, **kwargs)


class Cash(models.Model):
    decision = models.ForeignKey(DecisionType, on_delete=models.CASCADE)
    company = models.ForeignKey(Companies, on_delete=models.CASCADE, null=True, blank=True)
    date_dealt = models.DateField(blank=False)
    cash_value = models.FloatField()
    cash_balance = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CashQueryset.as_manager()

    class Meta:
        db_table = "cash"
        verbose_name_plural = "Cash"

    def __str__(self):
        return f"{self.cash_value} - {self.decision} - {self.date_dealt}"

    def get_absolute_url(self):
        return reverse("portfolio:cash_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        current_balance = Cash.objects.all().latest('date_dealt').cash_balance

        # Increase or decrease depending on type
        if self.decision.value == 'Deposit' or self.decision.value == 'Dividend' or self.decision.value == 'Sold':
            self.cash_balance = current_balance + self.cash_value
        elif self.decision.value == 'Withdrawal' or self.decision.value == 'Fee' or self.decision.value == 'Bought':
            self.cash_balance = current_balance - self.cash_value
        else:
            pass

        super(Cash, self).save(*args, **kwargs)


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
    month_end_date = models.DateField()
    company = models.OneToOneField(Companies, on_delete=models.CASCADE, primary_key=True)
    num_shares = models.IntegerField()
    fees_paid = models.FloatField()
    stock_holding = models.FloatField()

    objects = PortfolioQueryset.as_manager()

    class Meta:
        db_table = "portfolio"
        verbose_name_plural = "Portfolio"

    def __str__(self):
        return f"{self.company} - {self.num_shares} - {self.current_stock_price}"


# class PositionPerformance(models.Model):
#     month_end_date = models.DateField()
#     company = models.OneToOneField(Companies, on_delete=models.CASCADE, primary_key=True)
#     num_shares_bought = models.IntegerField()
#     num_shares_bought = models.IntegerField()
#     num_shares_sold = models.IntegerField()
#     fees_paid = models.FloatField()
#     current_stock_price = models.FloatField()
#     cash_holding = models.FloatField()

#     objects = PortfolioQueryset.as_manager()

#     class Meta:
#         db_table = "position_performance"
#         verbose_name_plural = "Position Performance"

#     def __str__(self):
#         return f"{self.company} - {self.num_shares} - {self.current_stock_price}"
