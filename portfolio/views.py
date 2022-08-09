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
from plotly.subplots import make_subplots
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


def portfolio_overview_charts(request):

    error_message = None

    df = pd.DataFrame(
            list(Investments.objects.get_table_joined())
            )

    df["price"] = df["price"].astype(float)

    chart_plot = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "domain"}, {"type": "table"}],
        [{"type": "xy"}, {"type": "scene"}]],
        # specs=[[{"type": "domain"}], [{"type": "xy"}]],
        )

    labels = df['company__company_name'].values
    # print(labels)
    values = df['price'].values
    # print(values)

    chart_plot.add_trace(
        go.Pie(values=values, labels=labels),
        row=1, col=1
    )

    chart_plot.add_trace(
        go.Table(header=dict(
            values=['Price', 'Company Name'],
            fill_color='paleturquoise',
            align='left'),
            cells=dict(
                values=[df.price, df.company__company_name],
                fill_color='lavender', align='left')),
        row=1, col=2
    )

    chart_plot.add_trace(
        go.Scatter(x=[20, 30, 40], y=[50, 60, 70]),
        row=2, col=1
    )

    # chart_plot.update_layout(showlegend=False)

    # chart_plot = go.pie(
    #     df,
    #     values="price",
    #     labels="company__company_name",
    #     title="Test Chart",
    #     )

    # labels = df['company__company_name'].values
    # print(labels)
    # values = df['price'].values
    # print(values)

    # chart_plot = go.Pie(labels=labels, values=values)

    # chart_plot = go.Figure(data=[go.Pie(labels=labels, values=values)])

    # chart_plot = px.pie(
    #     df,
    #     values="price",
    #     names="company__company_name",
    #     title="Test Chart",
    #     )

    # plot_div = plot(
    #     {'data': chart_plot},
    #     output_type='div'
    #     )

    plot_div = chart_plot.to_html(full_html=False, include_plotlyjs='cdn')

    context = {
        "graph": plot_div,
        "error_message": error_message,
        }

    return render(request, 'portfolio/partials/charts.html', context)


def portfolio_single_chart(request):

    fig = px.bar(x=["a", "b", "c"], y=[1, 3, 2])

    # plot_div = fig.to_html(full_html=False, include_plotlyjs='cdn')

    plot_div = plot(fig, output_type='div')

    context = {
        "graph": plot_div,
        }

    return render(request, 'portfolio/partials/single-chart.html', context)


def portfolio_single_chart2(request):

    fig = px.bar(x=["a", "b", "c"], y=[1, 3, 2])

    # plot_div = fig.to_html(full_html=False, include_plotlyjs='cdn')

    plot_div = plot(fig, output_type='div')

    context = {
        "graph2": plot_div,
        }

    return render(request, 'portfolio/partials/single-chart2.html', context)
