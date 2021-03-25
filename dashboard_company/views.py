from django.views.generic import ListView, DetailView
from django.shortcuts import render
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from django.http import JsonResponse
from django.views import View

import plotly.express as px

from .models import DashboardCompany
from ancillary_info.models import Parameters, Companies
from share_prices.models import SharePrices
from financial_reports.models import FinancialReports
from calculated_stats.models import CalculatedStats
from .managers import get_image


pd.options.plotting.backend = "plotly"


class DashboardListView(ListView):
    model = DashboardCompany
    context_object_name = "company_list"
    template_name = "dashboard/dashboard_list.html"

    ordering = ["defensive_rank"]


class DashboardDetailView(DetailView):
    model = DashboardCompany
    context_object_name = "company"
    template_name = "dashboard/dashboard_detail.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # context['share_chart'] = _share_chart(self.kwargs['pk'])
        context['parameters'] = Parameters.objects.all()

        return context


def dashboard_table(request, pk, report_type):

    error_message = None
    # Get correct company id
    company_name = DashboardCompany.objects.filter(
        id=pk
        ).values()[0]["company_name"]
    company_id = Companies.objects.filter(
        company_name=company_name
        ).values()[0]["id"]

    # Get financial data
    finance_qs = FinancialReports.objects.select_related("parameter_id").filter(
        company_id=company_id,
        parameter_id__report_section_id__report_type_id__report_name=report_type,
    )

    finance_data = finance_qs.values(
        "id", "time_stamp", "parameter_id__param_name", "value"
    )

    finance_df = pd.DataFrame(finance_data)

    finance_df = finance_df.drop_duplicates(
        subset=["time_stamp", "parameter_id__param_name"], keep="last"
    )

    finance_df_pivot = finance_df.pivot(
        columns="time_stamp",
        index="parameter_id__param_name",
        values="value",
    )

    context = {
        "finance_table": finance_df_pivot.to_html(classes="table", border=0),
        "report_type": report_type,
        "error_message": error_message,
    }

    return render(request, "dashboard/dashboard_table.html", context)


def dashboard_chart(request, pk):

    error_message = None

    company_name = DashboardCompany.objects.filter(
        id=pk
        ).values()[0]["company_name"]
    company_id = Companies.objects.filter(
        company_name=company_name
        ).values()[0]["id"]

    # share_chart = _share_chart(
    #     company_id
    # )
    # eps_chart = _param_chart(
    #     company_id, FinancialReports, "EPS norm. continuous"
    # )
    # dividend_chart = _param_chart(
    #     company_id, FinancialReports, "Dividend (adjusted) ps"
    # )
    roe_chart = _param_chart(
        company_id, CalculatedStats, "Return on Equity (ROE)"
    )
    equity_chart = _param_chart(
        company_id, CalculatedStats, "Equity (Book Value) Per Share"
    )
    roce_chart = _param_chart(company_id, CalculatedStats, "ROCE")
    total_chart = _multi_chart(
        company_id,
        FinancialReports,
        chart_name_1="Post-tax profit",
        chart_name_2="Total equity",
        chart_name_3="Total liabilities",
    )
    current_chart = _multi_chart(
        company_id,
        FinancialReports,
        chart_name_1="Post-tax profit",
        chart_name_2="Current assets",
        chart_name_3="Current liabilities",
    )

    context = {
        # "share_chart": share_chart,
        # "eps_chart": eps_chart,
        # "dividend_chart": dividend_chart,
        "roe_chart": roe_chart,
        "equity_chart": equity_chart,
        "roce_chart": roce_chart,
        "error_message": error_message,
        "total_chart": total_chart,
        "current_chart": current_chart,
    }

    return render(request, "dashboard/dashboard_chart.html", context)


def _param_chart(company_id, DataSource, param_name):
    param_id = Parameters.objects.filter(
        param_name=param_name
        ).values()[0]["id"]
    df = pd.DataFrame(
        DataSource.objects.filter(
            company_id=company_id, parameter_id=param_id
        ).values()
    )
    df["value"] = df["value"].astype(float)

    fig = px.line(
        df,
        x="time_stamp",
        y="value",
        title=param_name,
        labels={
            "time_stamp": "Date",
            "value": "pence",
        },
    )
    fig_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return fig_div


def _multi_chart(company_id, DataSource, *args, **kwargs):
    param_name_1 = kwargs["chart_name_1"]
    param_name_2 = kwargs["chart_name_2"]
    param_name_3 = kwargs["chart_name_3"]

    param_id_1 = Parameters.objects.filter(
        param_name=param_name_1
        ).values()[0]["id"]
    param_id_2 = Parameters.objects.filter(
        param_name=param_name_2
        ).values()[0]["id"]
    param_id_3 = Parameters.objects.filter(
        param_name=param_name_3
        ).values()[0]["id"]

    df_1 = pd.DataFrame(
        DataSource.objects.filter(
            company_id=company_id, parameter_id=param_id_1
        ).values()
    )
    df_3 = pd.DataFrame(
        DataSource.objects.filter(
            company_id=company_id, parameter_id=param_id_2
        ).values()
    )
    df_2 = pd.DataFrame(
        DataSource.objects.filter(
            company_id=company_id, parameter_id=param_id_3
        ).values()
    )

    df = pd.concat([df_1, df_2, df_3])
    # print(df)
    df["value"] = df["value"].astype(float)
    plt.switch_backend("Agg")
    plt.xticks(rotation=45)
    sns.lineplot(x="time_stamp", y="value", markers=True, data=df, hue="parameter_id")
    plt.title(param_name_1)
    plt.tight_layout()
    chart = get_image(plt)
    return chart


class ShareChartDataView(View):

    def get(self, request, pk):
        company_name = DashboardCompany.objects.filter(
            id=pk
            ).values()[0]["company_name"]
        company_id = Companies.objects.filter(
            company_name=company_name
            ).values()[0]["id"]
        share_qs = SharePrices.objects.filter(
            company_id=company_id
            ).values()

        y_data = []
        x_data = []

        for item in share_qs:
            y_data.append(item["value"])
            x_data.append(item["time_stamp"])

        y_data.reverse()
        x_data.reverse()
        data = {
            "x_data": x_data,
            "y_data": y_data,
        }

        return JsonResponse(data)


class EpsNormDataView(View):

    def get(self, request, pk):

        company_name = DashboardCompany.objects.filter(
            id=pk
            ).values()[0]["company_name"]
        company_id = Companies.objects.filter(
            company_name=company_name
            ).values()[0]["id"]
        param_id = Parameters.objects.filter(
            param_name="EPS norm. continuous"
            ).values()[0]["id"]

        df = pd.DataFrame(
            FinancialReports.objects.filter(
                company_id=company_id, parameter_id=param_id
            ).values()
        )
        df["value"] = df["value"].astype(float)

        y_data = []
        x_data = []

        for index, row in df.iterrows():
            y_data.append(row['value'])
            x_data.append(row['time_stamp'])

        data = {
            "x_data": x_data,
            "y_data": y_data,
        }

        return JsonResponse(data)


class DividendDataView(View):

    def get(self, request, pk):

        company_name = DashboardCompany.objects.filter(
            id=pk
            ).values()[0]["company_name"]
        company_id = Companies.objects.filter(
            company_name=company_name
            ).values()[0]["id"]
        param_id = Parameters.objects.filter(
            param_name="Dividend (adjusted) ps"
            ).values()[0]["id"]

        df = pd.DataFrame(
            FinancialReports.objects.filter(
                company_id=company_id, parameter_id=param_id
            ).values()
        )
        df["value"] = df["value"].astype(float)

        y_data = []
        x_data = []

        for index, row in df.iterrows():
            y_data.append(row['value'])
            x_data.append(row['time_stamp'])

        data = {
            "x_data": x_data,
            "y_data": y_data,
        }
        print(data)
        return JsonResponse(data)
