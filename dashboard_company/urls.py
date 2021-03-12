from django.urls import path

from .views import ChartData, DashboardListView, DashboardDetailView, dashboard_chart

app_name = 'dashboard_company'

urlpatterns = [
    path("", DashboardListView.as_view(), name="dashboard_list"),
    path("<int:pk>/api/chart/data/", ChartData.as_view()),
    path("<int:pk>/", DashboardDetailView.as_view(), name="dashboard_detail"),
    path("chart/<int:pk>/", dashboard_chart, name='dashboard_chart'),
]
