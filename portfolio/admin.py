from django.contrib import admin

from .models import (
    Transactions,
    Cash,
    WishList,
    Portfolio,
)


class TransactionsAdmin(admin.ModelAdmin):
    fields = [
        "num_stock",
        "num_stock_balance",
        "date_dealt",
        "date_settled",
        "reference",
        "price",
        "fees",
    ]

    readonly_fields = [
        "company",
        "decision"
    ]


class CashAdmin(admin.ModelAdmin):
    fields = [
        "decision",
        "date_dealt",
        "cash_value",
        "company",
        ]

    readonly_fields = [
        "cash_balance",
    ]


class WishListAdmin(admin.ModelAdmin):
    fields = ["value"]


class PortfolioAdmin(admin.ModelAdmin):
    fields = ["value"]


admin.site.register(Transactions, TransactionsAdmin)
admin.site.register(Cash, CashAdmin)
admin.site.register(WishList, WishListAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
