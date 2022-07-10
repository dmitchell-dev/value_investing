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
from plotly.offline import plot
import plotly.graph_objects as go
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


def portfolio_overview_pie_view(request):

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

    # plot_div = plot(
    #     {'data': chart_plot},
    #     output_type='div'
    #     )

    plot_div = chart_plot.to_html(full_html=False, include_plotlyjs='cdn')

    context = {
        "graph": plot_div,
        "error_message": error_message,
        }

    return render(request, 'portfolio/partials/pie-chart.html', context)


def portfolio_overview_table_view(request):

    error_message = None

    df = pd.DataFrame(
            list(Investments.objects.get_table_joined())
            )

    df["price"] = df["price"].astype(float)

    chart_plot2 = px.pie(
        df,
        values="price",
        names="company__company_name",
        title="Test Chart",
        )

    # plot_div = plot(
    #     {'data': chart_plot},
    #     output_type='div'
    #     )

    plot_div2 = chart_plot2.to_html(full_html=False, include_plotlyjs='cdn')

    context = {
        "graph2": plot_div2,
        "error_message2": error_message,
        }

    return render(request, 'portfolio/partials/pie-chart-2.html', context)
