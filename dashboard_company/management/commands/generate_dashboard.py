from django.core.management.base import BaseCommand
from ancillary_info.models import Parameters, Companies
from financial_reports.models import FinancialReports
from calculated_stats.models import CalculatedStats
from ranking_stats.models import RankingStats
from django.db.models import Max, F
import pandas as pd


class Command(BaseCommand):
    help = "Generate dashboard data"

    def handle(self, *args, **kwargs):
        df_params = pd.DataFrame(
            list(Parameters.objects.get_parameters_joined())
            )
        df_companies = pd.DataFrame(
            list(Companies.objects.get_companies_joined())
            )
        df_finance_reports = pd.DataFrame(
            list(FinancialReports.objects.get_financial_data_joined())
            )
        df_calc_stats = pd.DataFrame(
            list(CalculatedStats.objects.get_table_joined())
            )
        df_rank_stats = pd.DataFrame(
            list(RankingStats.objects.get_table_joined())
            )

        df_test = pd.DataFrame(list(FinancialReports.objects.values('company__tidm', 'parameter').annotate(time_stamp=Max('time_stamp'))))
        print(df_test)

        FinancialReports.objects.annotate(max_date=Max('company__parameter__time_stamp')).filter(time_stamp=F('max_date'))

        df_finance_reports_pivot = df_finance_reports.pivot(
            columns="time_stamp",
            index="company__tidm",
            values="value",
        )
        df_finance_reports_pivot = df_finance_reports_pivot.astype(float)

        company_num = 0
        company_list = list(df_companies['tidm'])
        num_companies = len(company_list)
        for company in company_list:
            company_num = company_num + 1
            s = f"{company_num} of {num_companies}, {company}"
            print(s)

        # print(df_params)
        # print(df_companies)
        # print(df_finance_reports)
        # print(df_calc_stats)
        # print(df_rank_stats)
