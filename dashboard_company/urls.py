from django.urls import path

from .views import DashboardListView, DashboardDetailView

urlpatterns = [
    path("", DashboardListView.as_view(), name="dashboard_list"),
    path("<int:pk>", DashboardDetailView.as_view(), name="dashboard_detail"),
]
