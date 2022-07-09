from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
    )
from django.shortcuts import render
from .models import Investments, WishList, Portfolio


class InvestmentListView(ListView):
    model = Investments
    context_object_name = "investment_list"
    template_name = "investments/investment_list.html"

    # ordering = ["margin_safety"]


class InvestmentDetailView(DetailView):
    model = Investments
    context_object_name = "investment"
    template_name = "investments/investment_detail.html"

    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get a context
    #     context = super().get_context_data(**kwargs)

    #     # Share Splits
    #     invest_pk = self.kwargs["pk"]
    #     comp_tidm = DashboardCompany.objects.get_tidm_from_id(comp_pk)
    #     share_splits = ShareSplits.objects.get_latest_date(comp_tidm)
    #     share_splits_last = None
    #     if share_splits:
    #         share_splits_last = share_splits.time_stamp

    #     # Add context data
    #     context["params"] = Params.objects.all()
    #     context["share_splits"] = share_splits_last

    #     return context


class InvestmentCreateView(CreateView):
    model = Investments
    template_name = "investments/investment_create.html"
    fields = [
        "company",
        "decision",
        "date_dealt",
        "date_settled",
        "reference",
        "num_stock",
        "price",
        "fees",
    ]


class InvestmentUpdateView(UpdateView):
    model = Investments
    template_name = "investments/investment_update.html"
    fields = [
        "company",
        "decision",
        "date_dealt",
        "date_settled",
        "reference",
        "num_stock",
        "price",
        "fees",
    ]


class InvestmentDeleteView(DeleteView):
    model = Investments
    template_name = "investments/investment_delete.html"
    success_url = reverse_lazy('portfolio:investment_list')
