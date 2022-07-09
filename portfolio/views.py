from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
    )
from django.shortcuts import render
from .models import Investments, WishList, Portfolio

import pandas as pd


class InvestmentListView(ListView):
    model = Investments
    context_object_name = "investment_list"
    template_name = "investments/investment_list.html"

    ordering = ["-date_dealt"]


class InvestmentDetailView(DetailView):
    model = Investments
    context_object_name = "investment"
    template_name = "investments/investment_detail.html"


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


class PortfolioOverviewView(TemplateView):

    template_name = "portfolio/overview.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        portfolio_data = self._get_portfolio_data()

        # Add context data
        context["investments"] = portfolio_data

        return context

    def _get_portfolio_data(self):
        test_df = Investments.objects.all()

        return test_df
