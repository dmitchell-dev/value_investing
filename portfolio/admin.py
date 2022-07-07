from django.contrib import admin

from .models import (
    Investments,
    WishList,
    Portfolio,
)


class InvestmentsAdmin(admin.ModelAdmin):
    fields = [
        "company__company_name",
        # "decision__decision_type",
        "num_stock",
        "date_dealt",
        "date_settled",
        "reference",
        "price",
        "fees",
    ]


class WishListAdmin(admin.ModelAdmin):
    fields = ["value"]


class PortfolioAdmin(admin.ModelAdmin):
    fields = ["value"]


admin.site.register(Investments, InvestmentsAdmin)
admin.site.register(WishList, WishListAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
