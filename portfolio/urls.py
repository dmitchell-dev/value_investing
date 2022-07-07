from django.urls import path, include

from .views import InvestmentListView, InvestmentDetailView

app_name = "portfolio"

urlpatterns = [
    path("investments/", InvestmentListView.as_view(), name="investment_list"),
    path("investments/<int:pk>/", InvestmentDetailView.as_view(), name="investment_detail"),
]
