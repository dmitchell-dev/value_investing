from django.core import management
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from django_tables2 import SingleTableView

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Companies, DcfVariables
from .tables import DCFTable, CompaniesTable


class CompanyListView(SingleTableView):
    model = Companies
    table_class = CompaniesTable
    template_name = "ancillary/company_list.html"

    ordering = ["company_name"]


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
    success_url = reverse_lazy("ancillary:company_list")


def company_stats_update(request, **kwargs):

    error_message = None
    pk = None

    for arg in kwargs.values():
        pk = arg

    # Import data for current company
    if pk:
        result_str = management.call_command("data_import", "--comp_pk", pk)
    else:
        result_str = management.call_command(
            "data_import",
        )

    # Get correct company name and tidm
    company_name = Companies.objects.filter(id=pk).values()[0]["company_name"]

    # Change to dict of dicts
    table_data = dict(x.split("; ") for x in result_str.split("-"))
    for key, value in table_data.items():
        table_data[key] = dict(x.split(": ") for x in value.split(", "))

    context = {
        "company_name": company_name,
        "result_str": result_str.split("-"),
        "table_data": table_data,
        "error_message": error_message,
    }
    messages.add_message(
        request, messages.SUCCESS, "Company stats were successfully updated."
    )

    return render(request, "ancillary/company_stats_update.html", context)


def company_all_stats_update(request, **kwargs):

    error_message = None

    result_str = management.call_command(
        "data_import",
    )

    # Change to dict of dicts
    table_data = dict(x.split("; ") for x in result_str.split("-"))
    for key, value in table_data.items():
        table_data[key] = dict(x.split(": ") for x in value.split(", "))

    context = {
        "result_str": result_str.split("-"),
        "table_data": table_data,
        "error_message": error_message,
    }

    messages.add_message(
        request, messages.SUCCESS, "Company stats were successfully updated."
    )

    return render(request, "ancillary/company_stats_update.html", context)


class DCFDetailView(DetailView):
    model = DcfVariables
    context_object_name = "DCFVariables"
    template_name = "ancillary/dcf_var_detail.html"


def dcf_var_detail(request, **kwargs):

    error_message = None
    pk = None

    for arg in kwargs.values():
        pk = arg

    # Get correct company name and tidm
    company_name = Companies.objects.filter(id=pk).values()[0]["company_name"]
    company_tidm = Companies.objects.filter(id=pk).values()[0]["tidm"]

    table = DCFTable(DcfVariables.objects.all().filter(company__tidm=company_tidm))
    company = Companies.objects.all().filter(tidm=company_tidm)

    context = {
        "company_name": company_name,
        "data": table,
        "company": company[0],
        "error_message": error_message,
    }

    return render(request, "ancillary/dcf_var_detail.html", context)


class DcfVariablesUpdateView(SuccessMessageMixin, UpdateView):
    model = DcfVariables
    template_name = "ancillary/dcf_var_update.html"
    fields = [
        "est_growth_rate",
        "est_disc_rate",
        "est_ltg_rate",
    ]

    def get_success_url(self):
        companyid = self.kwargs["pk"]
        return reverse_lazy("ancillary:dcf_var_detail", kwargs={"pk": companyid})

    success_message = "Company was updated successfully"
