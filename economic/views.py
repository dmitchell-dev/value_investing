from django.views.generic.base import TemplateView

from django.views import View


class CapeChartView(TemplateView):

    template_name = "economic/cape_chart.html"


class CapeChartDataView(View):
    def get(self, request):

        y_data = [1, 2, 3, 4]
        x_data = [5, 6, 7, 8]

        param_name = "Test CAPE"

        # for index, row in df.iterrows():
        #     y_data.append(row["value"])
        #     x_data.append(row["time_stamp"])

        data = {
            "x_data": x_data,
            "y_data": y_data,
            "param_name": param_name,
        }

        return data
