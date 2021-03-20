from django.urls import path

from .views import (
    ChartData,
    DashboardListView,
    DashboardDetailView,
    dashboard_chart,
    dashboard_table,
    dashboard_plotly)

app_name = 'dashboard_company'

urlpatterns = [
    path("", DashboardListView.as_view(), name="dashboard_list"),
    path("<int:pk>/api/chart/data/", ChartData.as_view()),
    path("<int:pk>/", DashboardDetailView.as_view(), name="dashboard_detail"),
    path("chart/<int:pk>/", dashboard_chart, name='dashboard_chart'),
    path("table/<int:pk>/<str:report_type>/", dashboard_table, name='dashboard_table'),
    path("plotly/<int:pk>/", dashboard_plotly, name='dashboard_plotly'),
]
