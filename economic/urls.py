from django.urls import path, include
from .views import CapeChartView, CapeChartDataView


app_name = "economic_data"

urlpatterns = [
    path("", CapeChartView.as_view(), name="cape_home"),
]

data_patterns = (
    [
        path("data/cape/", CapeChartDataView.as_view()),
    ],
    "data",
)

urlpatterns += [
    path("", include(data_patterns)),
]
