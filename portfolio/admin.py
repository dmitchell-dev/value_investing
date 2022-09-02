from django.contrib import admin

from .models import (
    Transactions,
    WishList,
    Portfolio,
)


class TransactionsAdmin(admin.ModelAdmin):
    fields = [
        "num_stock",
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


class WishListAdmin(admin.ModelAdmin):
    fields = ["value"]


class PortfolioAdmin(admin.ModelAdmin):
    fields = ["value"]


admin.site.register(Transactions, TransactionsAdmin)
admin.site.register(WishList, WishListAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
