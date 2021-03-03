from django.views.generic import ListView, DetailView
from django.shortcuts import render
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from .models import DashboardCompany
from share_prices.models import SharePrices
from .managers import get_image


class DashboardListView(ListView):
    model = DashboardCompany
    context_object_name = "company_list"
    template_name = 'dashboard/dashboard_list.html'


class DashboardDetailView(DetailView):
    model = DashboardCompany
    context_object_name = "company"
    template_name = 'dashboard/dashboard_detail.html'


def dashboard_chart(request, pk):

    error_message = None

    df = pd.DataFrame(SharePrices.objects.filter(company_id=pk).values())

    plt.switch_backend('Agg')
    plt.xticks(rotation=45)
    sns.lineplot(x='time_stamp', y='value', data=df)
    plt.title('Share Price')
    plt.tight_layout()
    graph = get_image()

    context = {
        'graph': graph,
        'error_message': error_message,
    }

    return render(request, 'dashboard/dashboard_chart.html', context)
