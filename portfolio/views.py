from django.urls import reverse_lazy, reverse
from django.shortcuts import render
from django.shortcuts import redirect

import django_tables2 as tables
from django_tables2 import SingleTableView

from django.views.generic.base import TemplateView
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from ancillary_info.models import Companies, DecisionType

from dashboard_company.models import DashboardCompany

from share_prices.models import SharePrices

from .models import Transactions, WishList, Cash

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
    current_stock_price = SharePrices.objects.get_latest_date(tidm).value_adjusted

    # Save company to database
    obj, created = WishList.objects.get_or_create(
        company_id=current_company.company_id,
        reporting_stock_price=reporting_stock_price,
        current_stock_price=current_stock_price,
        reporting_mos=reporting_mos,
        current_mos=latest_margin_of_safety,
        buy_mos=0.5,
    )

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

    pk = None

    for arg in kwargs.values():
        pk = arg

    # Delete company from wishlist
    try:
        # WishList.objects.filter(company_id=pk).delete()
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

    ordering = ["-date_dealt"]


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

    ordering = ["-date_dealt"]


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
        portfolio_sum_df = portfolio_df.groupby(["company__tidm", "decision__value"]).sum()
        portfolio_sum_df = portfolio_sum_df.reset_index()

        # Per Share Calculations
        # List of company ids
        comp_list = pd.unique(portfolio_df.company).tolist()
        df_companies = pd.DataFrame(list(Companies.objects.get_companies_joined()))
        df_dashboard = pd.DataFrame(list(DashboardCompany.objects.get_table_joined()))
        results_list = []
        tidm_list = []
        currency_symbol_list = []
        currency_value_list = []
        share_price_list = []
        for comp in comp_list:
            # Company and Dashboard ids and names
            comp_idx = df_companies[df_companies["id"] == comp].index[0]
            curr_tidm = df_companies["tidm"].iat[comp_idx]
            tidm_list.append(curr_tidm)
            dash_idx = df_dashboard[df_dashboard["tidm"] == curr_tidm].index[0]
            comp_id = df_dashboard["id"].iat[dash_idx]
            curr_comp_name = df_companies["company_name"].iat[comp_idx]
            curr_currency_symbol = df_companies["currency__symbol"].iat[comp_idx]
            currency_symbol_list.append(curr_currency_symbol)

            # Latest Share Price
            latest_share_price = df_dashboard["latest_share_price"].iat[dash_idx]
            curr_currency_value = df_companies["currency__value"].iat[comp_idx]
            currency_value_list.append(curr_currency_value)
            latest_share_price = latest_share_price * curr_currency_value
            share_price_list.append(latest_share_price)
            results_list.append({
                "tidm": curr_tidm,
                "company_name": curr_comp_name,
                "pk": comp_id,
                "latest_share_price": f"£{latest_share_price:.2f}"
                })

        # Info on cost and fees
        share_total_cost_list = []
        fees_list = []
        num_shares_list = []
        idx = 0

        buy_text = 'Bought'
        sell_text = 'Sold'

        for tidm in tidm_list:
            # Fee for transaction
            fee_bought = portfolio_sum_df[(portfolio_sum_df['company__tidm'] == tidm) & (portfolio_sum_df['decision__value'] == buy_text)].fees.sum()
            fee_sold = portfolio_sum_df[(portfolio_sum_df['company__tidm'] == tidm) & (portfolio_sum_df['decision__value'] == sell_text)].fees.sum()
            fee = fee_bought + fee_sold
            fees_list.append(fee)
            results_list[idx].update({"fees_paid": f"£{fee:.2f}"})

            # Share cost for transaction
            share_total_cost = portfolio_sum_df[(portfolio_sum_df['company__tidm'] == tidm) & (portfolio_sum_df['decision__value'] == buy_text)].price.sum()
            share_total_cost_list.append(share_total_cost)
            results_list[idx].update({"share_total_cost": f"£{share_total_cost:.2f}"})

            # Total cost for transaction
            total_cost = share_total_cost + fee
            total_cost_list = [a + b for a, b in zip(share_total_cost_list, fees_list)]
            results_list[idx].update({"total_cost": f"£{total_cost:.2f}"})

            # Number of shares
            num_shares_bought = portfolio_sum_df[(portfolio_sum_df['company__tidm'] == tidm) & (portfolio_sum_df['decision__value'] == buy_text)].num_stock.sum()
            num_shares_sold = portfolio_sum_df[(portfolio_sum_df['company__tidm'] == tidm) & (portfolio_sum_df['decision__value'] == sell_text)].num_stock.sum()
            num_shares = num_shares_bought - num_shares_sold
            num_shares_list.append(num_shares)
            results_list[idx].update({"number_shares_held": f"{num_shares}"})

            # Share price paid
            share_cost = share_total_cost / num_shares
            results_list[idx].update({"share_price_paid": f"£{share_cost:.2f}"})

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

        pct_change_list = [
            (a / b) * 100 for a, b in zip(value_change_list, total_cost_list)
        ]
        idx = 0
        for item in pct_change_list:
            results_list[idx].update({"pct_value_change": f"{item:.2f}%"})
            idx = idx + 1

        # Total Calculations
        total_dict = {}
        total_cost = portfolio_df.price.sum() + portfolio_df.fees.sum()
        total_dict["total_cost"] = f"£{total_cost:.2f}"
        total_fees = portfolio_df.fees.sum()
        total_dict["total_fees"] = f"£{total_fees:.2f}"
        pct_fees = (total_fees / (total_cost + total_fees)) * 100
        total_dict["total_pct_fees"] = f"{pct_fees:.2f}%"
        total_value = sum(total_value_list)
        total_dict["total_value"] = f"£{total_value:.2f}"
        total_value_change = sum(value_change_list)
        total_dict["total_value_change"] = f"£{total_value_change:.2f}"
        total_pct_value_change = ((total_value - total_cost) / total_cost) * 100
        total_dict["total_pct_value_change"] = f"{total_pct_value_change:.2f}%"

        # TODO get share price modal for selected company

        # Chart 1
        plot_div = value_pie_chart(portfolio_df)

        # Chart 2
        plot_div2 = perf_bar_chart(tidm_list, pct_change_list)

        # Results Table
        results_table = NameTable(results_list)
        print(results_table)

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
