from django.views.generic.base import TemplateView

from django.http import JsonResponse

from django.views import View

from share_prices.models import SharePrices
from calculated_stats.models import CalculatedStats
import pandas as pd


class CapeChartView(TemplateView):

    template_name = "economic/cape_chart.html"


class CapeChartDataView(View):
    def get(self, request):

        y_data = [1, 2, 3, 4]
        x_data = [5, 6, 7, 8]

        param_name = "Test CAPE"

        df = pd.DataFrame(CalculatedStats.objects.filter(parameter_id=225).values())
        print(df)

        # df = pd.DataFrame(SharePrices.objects.values())
        # print(df)

        # df['time_stamp'] = pd.to_datetime(df['time_stamp'], format='%Y-%m-%d')
        # print(df)

        # nov_mask = df['time_stamp'].map(lambda x: x.day) == 1
        # df = df[nov_mask]

        # print(df)

        df_pivot = df.pivot(
            columns="time_stamp",
            index="company_id",
            values="value",
        )
        
        df_pivot = df_pivot.astype(float)

        print(df_pivot)

        print(df_pivot.sum())

        # for index, row in df.iterrows():
        #     y_data.append(row["value"])
        #     x_data.append(row["time_stamp"])

        data = {
            "x_data": x_data,
            "y_data": y_data,
            "param_name": param_name,
        }

        return JsonResponse(data)
