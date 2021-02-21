from django.views.generic import ListView, DetailView

from .models import DashboardCompany


class DashboardListView(ListView):
    model = DashboardCompany
    context_object_name = "company_list"
    template_name = 'dashboard/dashboard_list.html'


class DashboardDetailView(DetailView):
    model = DashboardCompany
    context_object_name = "company"
    template_name = 'dashboard/dashboard_detail.html'
