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
from calculated_stats.models import DcfVariables

import pandas as pd


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


def company_stats_update(request, **kwargs):

    error_message = None
    pk = None

    for arg in kwargs.values():
        pk = arg

    # Import data for current company
    if pk:
        result_str = management.call_command(
            'data_import',
            '--comp_pk', pk
            )
    else:
        result_str = management.call_command(
            'data_import',
            )

    # Get correct company name and tidm
    company_name = Companies.objects.filter(id=pk).values()[0]["company_name"]

    context = {
        "company_name": company_name,
        "result_str": result_str.split('-'),
        "error_message": error_message,
    }
    messages.add_message(
        request,
        messages.SUCCESS,
        'Company stats were successfully updated.'
        )

    return render(request, "ancillary/company_stats_update.html", context)


def company_dcf_update(request, **kwargs):

    error_message = None
    pk = None

    for arg in kwargs.values():
        pk = arg

    # Get correct company name and tidm
    company_name = Companies.objects.filter(id=pk).values()[0]["company_name"]

    context = {
        "company_name": company_name,
        "error_message": error_message,
    }
    messages.add_message(
        request,
        messages.SUCCESS,
        'Company stats were successfully updated.'
        )

    return render(request, "ancillary/company_dcf_update.html", context)
