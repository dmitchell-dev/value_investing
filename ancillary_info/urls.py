from django.urls import path

from .views import (
    CompanyListView,
    CompanyDetailView,
    CompanyCreateView,
    CompanyUpdateView,
    CompanyDeleteView,
    dcf_var_detail,
    dcf_var_update,
    company_stats_update,
    )

app_name = "ancillary"

urlpatterns = [
    path("companies/<int:pk>/delete/", CompanyDeleteView.as_view(), name="company_delete"),
    path("companies/create/", CompanyCreateView.as_view(), name="company_create"),
    path("companies/<int:pk>/", CompanyDetailView.as_view(), name="company_detail"),
    path("companies/<int:pk>/update/", CompanyUpdateView.as_view(), name="company_update"),
    path("companies/<int:pk>/stats-update/", company_stats_update, name="company_stats_update"),
    path("companies/<int:pk>/dcf-update/", dcf_var_update, name="dcf_var_update"),
    path("companies/<int:pk>/dcf-detail/", dcf_var_detail, name="dcf_var_detail"),
    path("companies/ind-stats-update/", company_stats_update, name="company_ind_stats_update"),
    path("companies/", CompanyListView.as_view(), name="company_list"),
]
