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

import plotly.express as px
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

        portfolio_df = self._get_portfolio_data()

        # Add context data
        context["investments"] = portfolio_df

        return context

    def _get_portfolio_data(self):
        test_df = pd.DataFrame(
            list(Investments.objects.get_table_joined())
            )

        return test_df


def portfolio_overview_view(request):

    error_message = None

    df = pd.DataFrame(
            list(Investments.objects.get_table_joined())
            )

    df["price"] = df["price"].astype(float)

    chart_plot = px.pie(
        df,
        values="price",
        names="company__company_name",
        title="Test Chart",
    )

    # Getting HTML needed to render the plot.
    plot_div = chart_plot.to_html()

    context = {
        "graph": plot_div,
        "error_message": error_message,
    }

    return render(request, 'portfolio/partials/pie-chart.html', context)

    # if request.htmx:
    #     return render(request, 'portfolio/partials/pie-chart.html', context)
    # else:
    #     return render(request, 'portfolio/overview.html', context)
