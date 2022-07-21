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

    try:
        management.call_command('financial_reports_import', '--symbol', company_tidm)
        context = {
            "company_name": company_name,
            "company_tidm": company_tidm,
            "error_message": error_message,
        }
        messages.add_message(request, messages.SUCCESS, 'Company stats were successfully updated.')

    except Exception as e:
        messages.add_message(request, messages.ERROR, f"{str(e)}")
        return render(request, "ancillary/company_stats_update.html")

    return render(request, "ancillary/company_stats_update.html", context)
