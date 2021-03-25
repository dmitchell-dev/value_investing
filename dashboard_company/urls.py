from django.urls import path, include

from .views import (
    ShareChartDataView,
    EpsNormDataView,
    DividendDataView,
    DashboardListView,
    DashboardDetailView,
    dashboard_chart,
    dashboard_table,
)

app_name = "dashboard_company"

urlpatterns = [
    path("", DashboardListView.as_view(), name="dashboard_list"),
    path("<int:pk>/chart/", dashboard_chart, name="dashboard_chart"),
    path("<int:pk>/", DashboardDetailView.as_view(), name="dashboard_detail"),
    path("table/<int:pk>/<str:report_type>/", dashboard_table, name="dashboard_table"),
]

data_patterns = (
    [
        path("<int:pk>/chart/data/share-price/", ShareChartDataView.as_view()),
        path("<int:pk>/chart/data/eps-norm/", EpsNormDataView.as_view()),
        path("<int:pk>/chart/data/dividend/", DividendDataView.as_view()),
    ],
    "data",
)

urlpatterns += [
    path("", include(data_patterns)),
]
