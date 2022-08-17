from django.urls import reverse_lazy
from django.shortcuts import render

import django_tables2 as tables

from django.views.generic.base import TemplateView
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
    )

from ancillary_info.models import (
    Companies
)

from dashboard_company.models import (
    DashboardCompany
)

from share_prices.models import (
    SharePrices
)

from .models import (
    Investments,
    WishList,
    Portfolio
    )

from .managers import (
    value_pie_chart,
    perf_bar_chart,
    )

from .tables import (
    NameTable,
)

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
        portfolio_sum_df = portfolio_df.groupby(['company__tidm']).sum()

        # Per Share Calculations
        # List of company ids
        comp_list = pd.unique(portfolio_df.company).tolist()
        df_companies = pd.DataFrame(list(Companies.objects.get_companies_joined()))
        df_dashboard = pd.DataFrame(list(DashboardCompany.objects.get_table_joined()))
        results_list = []
        tidm_list = []
        currency_list = []
        for comp in comp_list:
            comp_idx = df_companies[df_companies['id'] == comp].index[0]
            curr_tidm = df_companies["tidm"].iat[comp_idx]
            dash_idx = df_dashboard[df_dashboard['tidm'] == curr_tidm].index[0]
            comp_id = df_dashboard["id"].iat[dash_idx]
            curr_comp_name = df_companies["company_name"].iat[comp_idx]
            curr_currency = df_companies["currency__value"].iat[comp_idx]
            tidm_list.append(curr_tidm)
            currency_list.append(curr_currency)
            results_list.append({'tidm': curr_tidm, 'company_name': curr_comp_name, 'pk': comp_id})
            # results_list.append({'company_name': curr_comp_name})
            # results_list.append({'pk': comp_idx})

        # Current price
        share_price_list = []
        idx = 0
        for tidm in tidm_list:
            df_share_price = SharePrices.objects.get_latest_date(tidm).value_adjusted
            # Need to fix properly
            # TODO Also get exchange latest rate from API
            if idx == 1 or idx == 2:
                df_share_price = df_share_price * 0.82
            share_price_list.append(df_share_price)
            results_list[idx].update({"latest_share_price": f"£{df_share_price:.2f}"})
            idx = idx + 1

        # Info on cost and fees
        share_cost_list = []
        fees_list = []
        num_shares_list = []
        idx = 0

        for tidm in tidm_list:
            fee = portfolio_sum_df[portfolio_sum_df.index == tidm].fees[0]
            fees_list.append(fee)
            results_list[idx].update({"fees_paid": f"£{fee:.2f}"})

            share_cost = portfolio_sum_df[portfolio_sum_df.index == tidm].price[0]
            share_cost_list.append(share_cost)
            results_list[idx].update({"share_price_paid": f"£{share_cost:.2f}"})

            total_cost_list = [a + b for a, b in zip(share_cost_list, fees_list)]

            num_shares = portfolio_sum_df[portfolio_sum_df.index == tidm].num_stock[0]
            num_shares_list.append(num_shares)
            results_list[idx].update({"number_shares_held": f"{num_shares}"})

            idx = idx + 1

        # calculate total % and value decrease/increase
        # total_value = price_list * num_shares
        total_value_list = [a * b for a, b in zip(share_price_list, num_shares_list)]
        idx = 0
        for item in total_value_list:
            results_list[idx].update({"latest_total_value": f"£{item:.2f}"})
            idx = idx + 1

        # pct_change = (total_value - cost_list) / cost_list
        value_change_list = [a - b for a, b in zip(total_value_list, total_cost_list)]
        idx = 0
        for item in value_change_list:
            results_list[idx].update({"value_change": f"£{item:.2f}"})
            idx = idx + 1

        pct_change_list = [(a / b)*100 for a, b in zip(value_change_list, total_cost_list)]
        idx = 0
        for item in pct_change_list:
            results_list[idx].update({"pct_value_change": f"{item:.2f}%"})
            idx = idx + 1

        # Total Calculations
        total_dict = {}
        total_cost = portfolio_df.price.sum()
        total_dict["total_cost"] = f"£{total_cost:.2f}"
        total_fees = portfolio_df.fees.sum()
        total_dict["total_fees"] = f"£{total_fees:.2f}"
        pct_fees = (total_fees / (total_cost + total_fees)) * 100
        total_dict["total_pct_fees"] = f"{pct_fees:.2f}%"
        total_value = sum(total_value_list)
        total_dict["total_value"] = f"£{total_value:.2f}"
        total_value_change = sum(value_change_list)
        total_dict["total_value_change"] = f"£{total_value_change:.2f}"
        total_pct_value_change = ((total_value - total_cost) / total_cost)* 100
        total_dict["total_pct_value_change"] = f"{total_pct_value_change:.2f}%"

        # TODO get share price modal for selected company

        # Chart 1
        plot_div = value_pie_chart(portfolio_df)

        # Chart 2
        plot_div2 = perf_bar_chart(tidm_list, pct_change_list)

        # Results Table
        results_table = NameTable(results_list)
        print(results_table)

        # context["investments"] = portfolio_df
        context["results_table"] = results_table
        context["total_dict"] = total_dict
        context["graph"] = plot_div
        context["graph2"] = plot_div2

        return context

    def _get_portfolio_data(self):
        test_df = pd.DataFrame(
            list(Investments.objects.get_table_joined())
            )

        test_df["price"] = test_df["price"].astype(float)
        test_df["fees"] = test_df["fees"].astype(float)

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

    fig = px.bar(x=["a", "b", "c"], y=[1, 2, 3])

    # plot_div = fig.to_html(full_html=False, include_plotlyjs='cdn')

    plot_div = plot(fig, output_type='div')

    context = {
        "graph": plot_div,
        }

    return render(request, 'portfolio/partials/single-chart.html', context)


def portfolio_single_chart2(request):

    fig = px.bar(x=["a", "b", "c"], y=[3, 2, 1])

    # plot_div = fig.to_html(full_html=False, include_plotlyjs='cdn')

    plot_div = plot(fig, output_type='div')

    print(plot_div)

    context = {
        "graph2": plot_div,
        }

    return render(request, 'portfolio/partials/single-chart2.html', context)
