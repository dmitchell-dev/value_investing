from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView
from django.shortcuts import render

from django.core.paginator import Paginator

import pandas as pd

from django.http import JsonResponse
from django.views import View

from .models import DashboardCompany
from ancillary_info.models import Params, Companies
from share_prices.models import SharePrices
from financial_reports.models import FinancialReports
from calculated_stats.models import CalculatedStats


pd.options.plotting.backend = "plotly"


class DashboardListView(ListView):
    model = DashboardCompany
    context_object_name = "company_list"
    template_name = "dashboard/dashboard_list.html"

    ordering = ["margin_safety"]


class DashboardDetailView(DetailView):
    model = DashboardCompany
    context_object_name = "company"
    template_name = "dashboard/dashboard_detail.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # context['share_chart'] = _share_chart(self.kwargs['pk'])
        context["params"] = Params.objects.all()

        return context


class DashboardTableView(TemplateView):

    template_name = "dashboard/dashboard_table_pagination.html"

    def get_context_data(self, pk, **kwargs):
        error_message = None
        # Get correct company id
        company_name = DashboardCompany.objects.filter(id=pk).values()[0][
            "company_name"
        ]
        company_id = Companies.objects.filter(company_name=company_name).values()[0][
            "id"
        ]

        report_type = "Income Statement"

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

        records = finance_df_pivot.to_dict(orient="records")

        paginator = Paginator(records, 10)
        page = self.request.GET.get("page")
        records = paginator.get_page(page)
        print(records)
        context = {
            "records": records,
            "report_type": report_type,
            "error_message": error_message,
        }
        return context


def dashboard_table(request, pk, report_type):

    error_message = None
    # Get correct company id
    company_name = DashboardCompany.objects.filter(id=pk).values()[0]["company_name"]
    company_id = Companies.objects.filter(company_name=company_name).values()[0]["id"]

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

    context = {
        "error_message": error_message,
    }

    return render(request, "dashboard/dashboard_chart.html", context)


def _param_chart(company_id, DataSource, param_name):

    param_id = Params.objects.filter(param_name=param_name).values()[0]["id"]

    df = pd.DataFrame(
        DataSource.objects.filter(company_id=company_id, parameter_id=param_id).values()
    )
    df["value"] = df["value"].astype(float)

    y_data = []
    x_data = []

    for index, row in df.iterrows():
        y_data.append(row["value"])
        x_data.append(row["time_stamp"])

    data = {
        "x_data": x_data,
        "y_data": y_data,
        "param_name": param_name,
    }
    # print(data)
    return data


def _multi_chart(company_id, DataSource, *args, **kwargs):
    param_name_1 = kwargs["chart_name_1"]
    param_name_2 = kwargs["chart_name_2"]
    param_name_3 = kwargs["chart_name_3"]
    chart_title = kwargs["chart_title"]

    param_id_1 = Params.objects.filter(param_name=param_name_1).values()[0]["id"]
    param_id_2 = Params.objects.filter(param_name=param_name_2).values()[0]["id"]
    param_id_3 = Params.objects.filter(param_name=param_name_3).values()[0]["id"]

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

    df_1["value"] = df_1["value"].astype(float)
    df_2["value"] = df_2["value"].astype(float)
    df_3["value"] = df_3["value"].astype(float)

    df1_y_data = []
    df1_x_data = []
    df2_y_data = []
    df2_x_data = []
    df3_y_data = []
    df3_x_data = []

    for index, row in df_1.iterrows():
        df1_y_data.append(row["value"])
        df1_x_data.append(row["time_stamp"])
    for index, row in df_2.iterrows():
        df2_y_data.append(row["value"])
        df2_x_data.append(row["time_stamp"])
    for index, row in df_3.iterrows():
        df3_y_data.append(row["value"])
        df3_x_data.append(row["time_stamp"])

    data = {
        "df1_x_data": df1_x_data,
        "df1_y_data": df1_y_data,
        "df1_name": param_name_1,
        "df2_x_data": df2_x_data,
        "df2_y_data": df2_y_data,
        "df2_name": param_name_2,
        "df3_x_data": df3_x_data,
        "df3_y_data": df3_y_data,
        "df3_name": param_name_3,
        "chart_title": chart_title,
    }

    return data


def _pk_to_comp_id(pk):
    company_name = DashboardCompany.objects.filter(id=pk).values()[0]["company_name"]
    company_id = Companies.objects.filter(company_name=company_name).values()[0]["id"]

    return company_id


class ShareChartDataView(View):
    def get(self, request, pk):

        company_id = _pk_to_comp_id(pk)

        share_qs = SharePrices.objects.filter(company_id=company_id).values()

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
            "param_name": "Share Price",
        }

        return JsonResponse(data)


class EpsNormDataView(View):
    def get(self, request, pk):

        company_id = _pk_to_comp_id(pk)

        data = _param_chart(company_id, FinancialReports, "Reported EPS")

        return JsonResponse(data)


class DividendDataView(View):
    def get(self, request, pk):

        company_id = _pk_to_comp_id(pk)

        data = _param_chart(company_id, CalculatedStats, "Dividends Per Share")
        print(data)

        return JsonResponse(data)


class RoeDataView(View):
    def get(self, request, pk):

        company_id = _pk_to_comp_id(pk)

        data = _param_chart(company_id, CalculatedStats, "Return on Equity (ROE)")

        return JsonResponse(data)


class BookValueDataView(View):
    def get(self, request, pk):

        company_id = _pk_to_comp_id(pk)

        data = _param_chart(
            company_id, CalculatedStats, "Equity (Book Value) Per Share"
        )

        return JsonResponse(data)


class RoceDataView(View):
    def get(self, request, pk):

        company_id = _pk_to_comp_id(pk)

        data = _param_chart(company_id, CalculatedStats, "Return on Capital Employed (ROCE)")

        return JsonResponse(data)


class DebtToEquityDataView(View):
    def get(self, request, pk):

        company_id = _pk_to_comp_id(pk)

        data = _param_chart(company_id, CalculatedStats, "Debt to Equity (D/E)")

        return JsonResponse(data)


class DividendCoverDataView(View):
    def get(self, request, pk):

        company_id = _pk_to_comp_id(pk)

        data = _param_chart(company_id, CalculatedStats, "Dividend Cover")

        return JsonResponse(data)


class PriceToEarningsDataView(View):
    def get(self, request, pk):

        company_id = _pk_to_comp_id(pk)

        data = _param_chart(company_id, CalculatedStats, "Price to Earnings (P/E)")

        return JsonResponse(data)


class PriceToBookValueDataView(View):
    def get(self, request, pk):

        company_id = _pk_to_comp_id(pk)

        data = _param_chart(company_id, CalculatedStats, "Price to Book Value (Equity)")

        return JsonResponse(data)


class IntrinsicValueDataView(View):
    def get(self, request, pk):

        company_id = _pk_to_comp_id(pk)

        data = _param_chart(company_id, CalculatedStats, "Intrinsic Value")

        return JsonResponse(data)


class AnnualYieldDataView(View):
    def get(self, request, pk):

        company_id = _pk_to_comp_id(pk)

        data = _param_chart(company_id, CalculatedStats, "Earnings Yield (Return)")

        return JsonResponse(data)


class FcfPsDataView(View):
    def get(self, request, pk):

        company_id = _pk_to_comp_id(pk)

        data = _param_chart(company_id, FinancialReports, "Free Cash Flow")

        return JsonResponse(data)


class CurrentRatioDataView(View):
    def get(self, request, pk):

        company_id = _pk_to_comp_id(pk)

        data = _param_chart(company_id, CalculatedStats, "Current Ratio")

        return JsonResponse(data)


class TotalMultiDataView(View):
    def get(self, request, pk):

        company_id = _pk_to_comp_id(pk)

        data = _multi_chart(
            company_id,
            FinancialReports,
            chart_name_1="Post-tax profit",
            chart_name_2="Total equity",
            chart_name_3="Total liabilities",
            chart_title="Total Charts",
        )

        return JsonResponse(data)


class CurrentMultiDataView(View):
    def get(self, request, pk):

        company_id = _pk_to_comp_id(pk)

        data = _multi_chart(
            company_id,
            FinancialReports,
            chart_name_1="Post-tax profit",
            chart_name_2="Current assets",
            chart_name_3="Current liabilities",
            chart_title="Current Charts",
        )

        return JsonResponse(data)
