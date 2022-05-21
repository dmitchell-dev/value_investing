from django.urls import path, include

from .views import (
    ShareChartDataView,
    EpsNormDataView,
    DividendDataView,
    DashboardListView,
    DashboardDetailView,
    RoeDataView,
    BookValueDataView,
    DebtToEquityDataView,
    RoceDataView,
    DividendCoverDataView,
    PriceToEarningsDataView,
    PriceToBookValueDataView,
    IntrinsicValueDataView,
    AnnualYieldDataView,
    FcfPsDataView,
    CurrentRatioDataView,
    TotalMultiDataView,
    CurrentMultiDataView,
    DashboardTableView,
    dashboard_chart,
    dashboard_table,
)

app_name = "dashboard_company"

urlpatterns = [
    path("", DashboardListView.as_view(), name="dashboard_list"),
    path("<int:pk>/chart/", dashboard_chart, name="dashboard_chart"),
    path("<int:pk>/", DashboardDetailView.as_view(), name="dashboard_detail"),
    path("table/<int:pk>/<str:report_type>/", dashboard_table, name="dashboard_table"),
    path(
        "<int:pk>/table-pag/",
        DashboardTableView.as_view(),
        name="dashboard_table_pagination",
    ),
]

data_patterns = (
    [
        path("<int:pk>/chart/data/share-price/", ShareChartDataView.as_view()),
        path("<int:pk>/chart/data/eps-norm/", EpsNormDataView.as_view()),
        path("<int:pk>/chart/data/dividend/", DividendDataView.as_view()),
        path("<int:pk>/chart/data/roe/", RoeDataView.as_view()),
        path("<int:pk>/chart/data/book-value/", BookValueDataView.as_view()),
        path("<int:pk>/chart/data/debt-to-equity/", DebtToEquityDataView.as_view()),
        path("<int:pk>/chart/data/dividend-cover/", DividendCoverDataView.as_view()),
        path("<int:pk>/chart/data/roce/", RoceDataView.as_view()),
        path(
            "<int:pk>/chart/data/price-to-earnings/", PriceToEarningsDataView.as_view()
        ),
        path(
            "<int:pk>/chart/data/price-to-bookvalue/",
            PriceToBookValueDataView.as_view(),
        ),
        path("<int:pk>/chart/data/intrinsic-value/", IntrinsicValueDataView.as_view()),
        path("<int:pk>/chart/data/annual-yield/", AnnualYieldDataView.as_view()),
        path("<int:pk>/chart/data/fcf-ps/", FcfPsDataView.as_view()),
        path("<int:pk>/chart/data/current-ratio/", CurrentRatioDataView.as_view()),
        path("<int:pk>/chart/data/total-multi/", TotalMultiDataView.as_view()),
        path("<int:pk>/chart/data/current-multi/", CurrentMultiDataView.as_view()),
    ],
    "data",
)

urlpatterns += [
    path("", include(data_patterns)),
]
