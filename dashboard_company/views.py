from django.views.generic import ListView, DetailView
from django.shortcuts import render
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from .models import DashboardCompany
from ancillary_info.models import Parameters, Companies
from share_prices.models import SharePrices
from financial_reports.models import FinancialReports
from calculated_stats.models import CalculatedStats
from .managers import get_image


class DashboardListView(ListView):
    model = DashboardCompany
    context_object_name = "company_list"
    template_name = 'dashboard/dashboard_list.html'

    ordering = ['defensive_rank']


class DashboardDetailView(DetailView):
    model = DashboardCompany
    context_object_name = "company"
    template_name = 'dashboard/dashboard_detail.html'


def dashboard_chart(request, pk):

    error_message = None

    company_name = DashboardCompany.objects.filter(
        id=pk
        ).values()[0]['company_name']
    company_id = Companies.objects.filter(
        company_name=company_name
        ).values()[0]['id']

    share_chart = _share_chart(company_id)
    eps_chart = _param_chart(
        company_id, FinancialReports, "EPS norm. continuous"
        )
    dividend_chart = _param_chart(
        company_id, FinancialReports, "Dividend (adjusted) ps"
        )
    roe_chart = _param_chart(
        company_id, CalculatedStats, "Return on Equity (ROE)"
        )
    equity_chart = _param_chart(
        company_id, CalculatedStats, "Equity (Book Value) Per Share"
        )
    roce_chart = _param_chart(
        company_id, CalculatedStats, "ROCE"
        )
    total_chart = _multi_chart(
        company_id,
        FinancialReports,
        chart_name_1="Post-tax profit",
        chart_name_2="Total equity",
        chart_name_3="Total liabilities"
        )
    current_chart = _multi_chart(
        company_id,
        FinancialReports,
        chart_name_1="Post-tax profit",
        chart_name_2="Current assets",
        chart_name_3="Current liabilities"
        )

    context = {
        'share_chart': share_chart,
        'eps_chart': eps_chart,
        'dividend_chart': dividend_chart,
        'roe_chart': roe_chart,
        'equity_chart': equity_chart,
        'roce_chart': roce_chart,
        'error_message': error_message,
        'total_chart': total_chart,
        'current_chart': current_chart,
    }

    return render(request, 'dashboard/dashboard_chart.html', context)


def _share_chart(company_id):
    df = pd.DataFrame(SharePrices.objects.filter(company_id=company_id).values())
    plt.switch_backend('Agg')
    plt.xticks(rotation=45)
    sns.lineplot(x='time_stamp', y='value', markers=True, data=df)
    plt.title('Share Price')
    plt.tight_layout()
    chart = get_image(plt)
    return chart


def _param_chart(company_id, DataSource, param_name):
    param_id = Parameters.objects.filter(
        param_name=param_name
        ).values()[0]['id']
    df = pd.DataFrame(DataSource.objects.filter(
        company_id=company_id, parameter_id=param_id
        ).values())
    df['value'] = df['value'].astype(float)
    plt.switch_backend('Agg')
    plt.xticks(rotation=45)
    sns.lineplot(x='time_stamp', y='value', markers=True, data=df)
    plt.title(param_name)
    plt.tight_layout()
    chart = get_image(plt)
    return chart


def _multi_chart(company_id, DataSource, *args, **kwargs):
    param_name_1 = kwargs['chart_name_1']
    param_name_2 = kwargs['chart_name_2']
    param_name_3 = kwargs['chart_name_3']

    param_id_1 = Parameters.objects.filter(
        param_name=param_name_1
        ).values()[0]['id']
    param_id_2 = Parameters.objects.filter(
        param_name=param_name_2
        ).values()[0]['id']
    param_id_3 = Parameters.objects.filter(
        param_name=param_name_3
        ).values()[0]['id']

    df_1 = pd.DataFrame(DataSource.objects.filter(
        company_id=company_id, parameter_id=param_id_1
        ).values())
    df_3 = pd.DataFrame(DataSource.objects.filter(
        company_id=company_id, parameter_id=param_id_2
        ).values())
    df_2 = pd.DataFrame(DataSource.objects.filter(
        company_id=company_id, parameter_id=param_id_3
        ).values())

    df = pd.concat([df_1, df_2, df_3])
    print(df)
    df['value'] = df['value'].astype(float)
    plt.switch_backend('Agg')
    plt.xticks(rotation=45)
    sns.lineplot(x='time_stamp', y='value', markers=True, data=df, hue="parameter_id")
    plt.title(param_name_1)
    plt.tight_layout()
    chart = get_image(plt)
    return chart
