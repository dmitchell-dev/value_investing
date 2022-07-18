from django.urls import reverse_lazy
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


class CompanyCreateView(CreateView):
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


class CompanyUpdateView(UpdateView):
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


class CompanyDeleteView(DeleteView):
    model = Companies
    template_name = "ancillary/company_delete.html"
    success_url = reverse_lazy('ancillary:company_list')
