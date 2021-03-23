from django.urls import path, include

from .views import (
    ShareChartDataView,
    DashboardListView,
    DashboardDetailView,
    dashboard_chart,
    dashboard_table,
)

app_name = "dashboard_company"

urlpatterns = [
    path("", DashboardListView.as_view(), name="dashboard_list"),
    path("<int:pk>/", DashboardDetailView.as_view(), name="dashboard_detail"),
    path("chart/<int:pk>/", dashboard_chart, name="dashboard_chart"),
    path("table/<int:pk>/<str:report_type>/", dashboard_table, name="dashboard_table"),
]

data_patterns = (
    [
        path("<int:pk>/api/chart/data/", ShareChartDataView.as_view()),
    ],
    "data",
)

urlpatterns += [
    path("", include(data_patterns)),
]
