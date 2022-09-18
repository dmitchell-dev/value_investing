from django.urls import reverse_lazy
from django.shortcuts import render
from django.shortcuts import redirect

from .forms import TransactionsForm

from django_tables2 import SingleTableView

from django.views.generic.base import TemplateView
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from dashboard_company.models import DashboardCompany

from share_prices.models import SharePrices

from .models import (
    Transactions,
    WishList,
    Cash,
    Portfolio,)

from .managers import (
    value_pie_chart,
    perf_bar_chart,
)

from .tables import (
    NameTable,
    WishListTable,
)

import plotly.express as px
from plotly.offline import plot
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from django.contrib import messages
import pandas as pd


class WishListListView(SingleTableView):
    model = WishList
    table_class = WishListTable
    template_name = "portfolio/wishlist_list.html"

    # ordering = ["margin_safety"]


class WishListDetailView(DetailView):
    model = WishList
    context_object_name = "wishlist"
    template_name = "portfolio/wishlist_detail.html"


class WishListDeleteView(DeleteView):
    model = WishList
    template_name = "portfolio/wishlist_delete.html"
    success_url = reverse_lazy("portfolio:wishlist_list")


class WishListUpdateView(UpdateView):
    model = WishList
    template_name = "portfolio/wishlist_update.html"
    fields = [
        # "reporting_stock_price",
        # "current_stock_price",
        # "reporting_mos",
        # "current_mos",
        "buy_mos",
    ]


def wish_list_create(request, **kwargs):

    pk = None

    for arg in kwargs.values():
        pk = arg

    # Get reporting and latest stats
    current_company = DashboardCompany.objects.filter(pk=pk)[0]
    tidm = current_company.tidm
    reporting_stock_price = current_company.share_price
    reporting_mos = current_company.margin_safety
    latest_margin_of_safety = current_company.latest_margin_of_safety
    latest_financial_date = current_company.latest_financial_date
    latest_share_price_date = current_company.latest_share_price_date
    current_stock_price = SharePrices.objects.get_latest_date(tidm).value_adjusted

    # Save company to database
    obj, created = WishList.objects.get_or_create(
        company_id=current_company.company_id,
        reporting_stock_price=reporting_stock_price,
        current_stock_price=current_stock_price,
        reporting_mos=reporting_mos,
        current_mos=latest_margin_of_safety,
        latest_financial_date=latest_financial_date,
        latest_share_price_date=latest_share_price_date,
        buy_mos=0.5,
    )

    # Update Decision Type = "Wish List"
    DashboardCompany.objects.filter(pk=pk).update(decision_type=2)

    if created:
        messages.add_message(
            request, messages.SUCCESS, "Company successfully added to wish list."
        )
    else:
        messages.add_message(
            request, messages.WARNING, "Company already exists on the wish list."
        )

    return redirect('dashboard_company:dashboard_detail', pk=pk)


def wish_list_remove(request, **kwargs):

    dash_pk = None

    for arg in kwargs.values():
        pk = arg

    # Update Decision Type = "No"
    DashboardCompany.objects.filter(pk=pk).update(decision_type=1)

    # Delete company from wishlist
    try:
        WishList.objects.get(pk=pk).delete()
        messages.add_message(
            request, messages.SUCCESS, "Company successfully removed to wish list."
        )
    except WishList.DoesNotExist:
        messages.add_message(
            request, messages.WARNING, "Company does not exist on the wish list."
        )

    return redirect('dashboard_company:dashboard_detail', pk=pk)


class TransactionListView(ListView):
    model = Transactions
    context_object_name = "transaction_list"
    template_name = "transactions/transaction_list.html"

    ordering = ["date_dealt"]


class TransactionDetailView(DetailView):
    model = Transactions
    context_object_name = "transaction"
    template_name = "transactions/transaction_detail.html"


class TransactionCreateView(CreateView):
    model = Transactions
    template_name = "transactions/transaction_create.html"
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


def transaction_create_view(request):
    # dictionary for initial data with
    # field names as keys
    context = {}

    # add the dictionary during initialization
    form = TransactionsForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('portfolio:transaction_list')

        # TODO get pk
        # DashboardCompany.objects.filter(pk=pk).update(decision_type=3)

        # if created:
        #     messages.add_message(
        #         request, messages.SUCCESS, "Transaction successfully added."
        #     )
        # else:
        #     messages.add_message(
        #         request, messages.WARNING, "Transaction already exists."
        #     )

    context['form'] = form
    return render(request, "transactions/transaction_create.html", context)


class TransactionUpdateView(UpdateView):
    model = Transactions
    template_name = "transactions/transaction_update.html"
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


class TransactionDeleteView(DeleteView):
    model = Transactions
    template_name = "transactions/transaction_delete.html"
    success_url = reverse_lazy("portfolio:transaction_list")


class CashListView(ListView):
    model = Cash
    context_object_name = "cash_list"
    template_name = "cash/cash_list.html"

    ordering = ["date_dealt"]


class CashDetailView(DetailView):
    model = Cash
    context_object_name = "cash"
    template_name = "cash/cash_detail.html"


class CashCreateView(CreateView):
    model = Cash
    template_name = "cash/cash_create.html"
    fields = [
        "decision",
        "date_dealt",
        "cash_value",
        "company",
    ]


class CashUpdateView(UpdateView):
    model = Cash
    template_name = "cash/cash_update.html"
    fields = [
        "decision",
        "date_dealt",
        "cash_value",
        "company",
    ]


class CashDeleteView(DeleteView):
    model = Cash
    template_name = "cash/cash_delete.html"
    success_url = reverse_lazy("portfolio:cash_list")


class PortfolioOverviewView(TemplateView):

    template_name = "portfolio/overview.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        portfolio_df = self._get_portfolio_data()

        # Results Table
        results_df = pd.DataFrame(list(Portfolio.objects.get_table_joined()))
        results_dict = results_df.to_dict(orient="records")
        results_table = NameTable(results_dict)

        total_dict = {}
        total_fees = results_df['fees_bought'].sum() + results_df['fees_sold'].sum()
        total_initial_value = results_df['initial_shares_cost'].sum()
        total_latest_value = results_df['latest_shares_holding'].sum()
        total_value_change = results_df['share_value_change'].sum()
        total_pct_value_change = ((total_latest_value - total_initial_value) / total_initial_value) * 100
        pct_fees = (total_fees / (total_initial_value + total_fees)) * 100
        income_from_selling = results_df['income_from_selling'].sum()
        total_profit = results_df['total_profit'].sum()
        total_pct_profit_change = ((income_from_selling - total_initial_value) / total_initial_value) * 100

        # Cash
        latest_cash_bal = Cash.objects.get_latest_balance()

        # Create Total Dictionary
        total_dict["total_initial_value"] = f"£{total_initial_value:.2f}"
        total_dict["total_fees"] = f"£{total_fees:.2f}"
        total_dict["total_pct_fees"] = f"{pct_fees:.1f}%"
        total_dict["total_latest_value"] = f"£{total_latest_value:.2f}"
        total_dict["total_value_change"] = f"£{total_value_change:.2f}"
        total_dict["total_pct_value_change"] = f"{total_pct_value_change:.1f}%"
        total_dict["income_from_selling"] = f"£{income_from_selling:.2f}"
        total_dict["total_profit"] = f"£{total_profit:.2f}"
        total_dict["total_pct_profit_change"] = f"{total_pct_profit_change:.1f}%"
        total_dict["latest_cash_bal"] = f"£{latest_cash_bal:.2f}"

        # Chart 1
        plot_div = value_pie_chart(results_df)

        # Chart 2
        tidm_list = results_df['company__tidm'].to_list()
        pct_change_list = results_df['share_pct_change'].to_list()
        plot_div2 = perf_bar_chart(tidm_list, pct_change_list)

        # Add context
        context["results_table"] = results_table
        context["total_dict"] = total_dict
        context["graph"] = plot_div
        context["graph2"] = plot_div2

        return context

    def _get_portfolio_data(self):
        transaction_df = pd.DataFrame(list(Transactions.objects.get_table_joined()))

        transaction_df["price"] = transaction_df["price"].astype(float)
        transaction_df["fees"] = transaction_df["fees"].astype(float)

        return transaction_df


def portfolio_overview_charts(request):

    error_message = None

    df = pd.DataFrame(list(Transactions.objects.get_table_joined()))

    df["price"] = df["price"].astype(float)

    chart_plot = make_subplots(
        rows=2,
        cols=2,
        specs=[
            [{"type": "domain"}, {"type": "table"}],
            [{"type": "xy"}, {"type": "scene"}],
        ],
        # specs=[[{"type": "domain"}], [{"type": "xy"}]],
    )

    labels = df["company__company_name"].values
    # print(labels)
    values = df["price"].values
    # print(values)

    chart_plot.add_trace(go.Pie(values=values, labels=labels), row=1, col=1)

    chart_plot.add_trace(
        go.Table(
            header=dict(
                values=["Price", "Company Name"],
                fill_color="paleturquoise",
                align="left",
            ),
            cells=dict(
                values=[df.price, df.company__company_name],
                fill_color="lavender",
                align="left",
            ),
        ),
        row=1,
        col=2,
    )

    chart_plot.add_trace(go.Scatter(x=[20, 30, 40], y=[50, 60, 70]), row=2, col=1)

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

    plot_div = chart_plot.to_html(full_html=False, include_plotlyjs="cdn")

    context = {
        "graph": plot_div,
        "error_message": error_message,
    }

    return render(request, "portfolio/partials/charts.html", context)


def portfolio_single_chart(request):

    fig = px.bar(x=["a", "b", "c"], y=[1, 2, 3])

    # plot_div = fig.to_html(full_html=False, include_plotlyjs='cdn')

    plot_div = plot(fig, output_type="div")

    context = {
        "graph": plot_div,
    }

    return render(request, "portfolio/partials/single-chart.html", context)


def portfolio_single_chart2(request):

    fig = px.bar(x=["a", "b", "c"], y=[3, 2, 1])

    # plot_div = fig.to_html(full_html=False, include_plotlyjs='cdn')

    plot_div = plot(fig, output_type="div")

    print(plot_div)

    context = {
        "graph2": plot_div,
    }

    return render(request, "portfolio/partials/single-chart2.html", context)
