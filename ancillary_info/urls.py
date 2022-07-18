from django.urls import path

from .views import (
    CompanyListView,
    CompanyDetailView,
    CompanyCreateView,
    CompanyUpdateView,
    CompanyDeleteView,
    )

app_name = "ancillary"

urlpatterns = [
    path("companies/<int:pk>/delete/", CompanyDeleteView.as_view(), name="company_delete"),
    path("companies/create/", CompanyCreateView.as_view(), name="company_create"),
    path("companies/<int:pk>/", CompanyDetailView.as_view(), name="company_detail"),
    path("companies/<int:pk>/update/", CompanyUpdateView.as_view(), name="company_update"),
    path("companies/", CompanyListView.as_view(), name="company_list"),
]
