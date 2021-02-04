import csv
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import AutoField

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

object_list = [
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
    help = 'Populates Static tables from csv files'

    def handle(self, *args, **kwargs):
        for table_object in object_list:

            table_name = table_object._meta.db_table

            all_fields = []
            for field in table_object._meta.fields:
                if not isinstance(field, AutoField):
                    all_fields.append(field.attname)
            print(all_fields)

            path = BASE_DIR_LOCAL / f"data/database_tables/{table_name}.csv"

            with open(path) as f:
                reader = csv.reader(f)
                next(reader, None)  # skip the header
                for row in reader:

                    insert_dict = {}
                    row_num = 0
                    # For cvs files with varying column numbers
                    for field in all_fields:
                        row_num = row_num + 1
                        insert_dict[field] = row[row_num]

                    _, created = table_object.objects.get_or_create(**insert_dict)
