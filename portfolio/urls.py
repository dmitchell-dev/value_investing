from django.urls import path, include

from .views import (
    InvestmentListView,
    InvestmentDetailView,
    InvestmentCreateView,
    InvestmentUpdateView,
    InvestmentDeleteView,
    PortfolioOverviewView,
    portfolio_overview_charts,
    )

app_name = "portfolio"

urlpatterns = [
    path("investments/<int:pk>/delete/", InvestmentDeleteView.as_view(), name="investment_delete"),
    path("investments/create/", InvestmentCreateView.as_view(), name="investment_create"),
    path("investments/<int:pk>/", InvestmentDetailView.as_view(), name="investment_detail"),
    path("investments/<int:pk>/update/", InvestmentUpdateView.as_view(), name="investment_update"),
    path("investments/", InvestmentListView.as_view(), name="investment_list"),
    path("overview/", PortfolioOverviewView.as_view(), name="portfolio_overview"),
    path("overview/charts/", portfolio_overview_charts, name="portfolio_charts"),
]
