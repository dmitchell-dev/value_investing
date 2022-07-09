from django.urls import path, include

from .views import (
    InvestmentListView,
    InvestmentDetailView,
    InvestmentCreateView,
    InvestmentUpdateView,
    )

app_name = "portfolio"

urlpatterns = [
    path("investments/create/", InvestmentCreateView.as_view(), name="investment_create"),
    path("investments/<int:pk>/update/", InvestmentUpdateView.as_view(), name="investment_update"),
    path("investments/<int:pk>/", InvestmentDetailView.as_view(), name="investment_detail"),
    path("investments/", InvestmentListView.as_view(), name="investment_list"),
]
