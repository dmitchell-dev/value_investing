from django.core import management
from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
    )
from .models import Companies


class CompanyListView(ListView):
    model = Companies
    context_object_name = "company_list"
    template_name = "ancillary/company_list.html"

    ordering = ["tidm"]


class CompanyDetailView(DetailView):
    model = Companies
    context_object_name = "company"
    template_name = "ancillary/company_detail.html"


class CompanyCreateView(SuccessMessageMixin, CreateView):
    model = Companies
    template_name = "ancillary/company_create.html"
    fields = [
        "company_name",
        "tidm",
        "comp_type",
        "sector",
        "industry",
        "exchange",
        "country",
        "currency",
        "company_source",
        "wish_list",
        "company_summary",
    ]

    success_message = "Company was created successfully"


class CompanyUpdateView(SuccessMessageMixin, UpdateView):
    model = Companies
    template_name = "ancillary/company_update.html"
    fields = [
        "company_name",
        "tidm",
        "comp_type",
        "sector",
        "industry",
        "exchange",
        "country",
        "currency",
        "company_source",
        "wish_list",
        "company_summary",
    ]

    success_message = "Company was updated successfully"


class CompanyDeleteView(DeleteView):
    model = Companies
    template_name = "ancillary/company_delete.html"
    success_url = reverse_lazy('ancillary:company_list')


def company_stats_update(request, pk):

    error_message = None
    # Get correct company name and tidm
    company_name = Companies.objects.filter(id=pk).values()[0]["company_name"]
    company_tidm = Companies.objects.filter(id=pk).values()[0]["tidm"]

    # try:

    reports_num = management.call_command(
        'financial_reports_import',
        '--symbol', company_tidm
        )

    reports_av_num = management.call_command(
        'financial_reports_import_av',
        '--symbol', company_tidm
        )

    share_price_num = management.call_command(
        'share_price_import_av',
        '--symbol', company_tidm
        )

    share_split_num = management.call_command(
        'share_split_calcs',
        '--symbol', company_tidm
        )

    default_var_num = management.call_command(
        'detault_dfc_variables',
        '--symbol', company_tidm
        )

    calc_stats_num = management.call_command(
        'calculate_stats',
        '--symbol', company_tidm
        )

    (dash_created, dash_updated) = management.call_command(
        'generate_dashboard'
        )

    context = {
        "company_name": company_name,
        "company_tidm": company_tidm,
        "error_message": error_message,
    }
    messages.add_message(
        request,
        messages.SUCCESS,
        'Company stats were successfully updated.'
        )

    print("###### SUMMARY UPDATE STATS ROWS ADDED ######")
    print(f"Financial Reports: {reports_num}")
    print(f"Financial Reports Alpha Vantage: {reports_av_num}")
    print(f"Share Price Alpha Vantage: {share_price_num}")
    print(f"Share Split: {share_split_num}")
    print(f"Default Variables: {default_var_num}")
    print(f"Calculate Stats: {calc_stats_num}")
    print(f"Dashboard Created: {dash_created}")
    print(f"Dashboard Updated: {dash_updated}")

    # except Exception as e:
        # messages.add_message(request, messages.ERROR, f"{str(e)}")

        # return render(request, "ancillary/company_stats_update.html")

    return render(request, "ancillary/company_stats_update.html", context)
