import csv
import itertools
from value_investing.settings import BASE_DIR
from django.conf import settings
from django.core.management.base import BaseCommand
from ancillary_info.models import (
        Markets,
        CompanyType,
        IndustryRisk,
        ReportType,
        Industries,
        ReportSection,
        Parameters,
        CalcVariables,
        Companies,
    )

table_list = [
    Markets,
    CompanyType,
    IndustryRisk,
    ReportType,
    Industries,
    ReportSection,
    Parameters,
    CalcVariables,
    Companies,
]

BASE_DIR_LOCAL = settings.BASE_DIR


class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
        # table_name = Markets._meta.db_table

        # path = BASE_DIR_LOCAL / f"data/database_tables/{table_name}.csv"

        # with open(path) as f:
        #     reader = csv.reader(f)
        #     row_count = sum(1 for row in reader)
        #     for row in reader:
        #         _, created = Markets.objects.get_or_create(
        #             share_listing=row[1]
        #             )
        #         print(created)
        #     print(row_count)

        # with open(path) as f:
        #     reader1, reader2 = itertools.tee(csv.reader(f))
        #     columns = len(next(reader1))
        #     del reader1
        #     for row in reader2:
        #         _, created = Markets.objects.get_or_create(
        #             share_listing=row[1]
        #             )
        #         print(created)
        #     print(columns)

        for table_object in table_list:

            table_name = table_object._meta.db_table
            all_fields = [f.name for f in table_object._meta.fields][1:]
            print(all_fields)

            path = BASE_DIR_LOCAL / f"data/database_tables/{table_name}.csv"

            with open(path) as f:
                reader = csv.reader(f)
                for row in reader:

                    insert_dict = {}
                    row_num = 0
                    for field in all_fields:
                        row_num = row_num + 1
                        insert_dict[field] = row[row_num]

                    _, created = table_object.objects.get_or_create(**insert_dict)
                    print(created)
