import csv
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import AutoField

from ancillary_info.models import (
    Exchanges,
    CompanyType,
    Industries,
    Sectors,
    Currencies,
    Countries,
    ReportType,
    Params,
    Datasource,
    CompSource,
    ParamsApi,
    Companies,
    DecisionType,
)

object_list = [
    Exchanges,
    CompanyType,
    Industries,
    Sectors,
    Currencies,
    Countries,
    ReportType,
    Params,
    Datasource,
    CompSource,
    ParamsApi,
    Companies,
    DecisionType,
]

BASE_DIR_LOCAL = settings.BASE_DIR


class Command(BaseCommand):
    help = "Populates Static tables from csv files"

    def handle(self, *args, **kwargs):

        results_list = []

        for table_object in object_list:

            table_name = table_object._meta.db_table

            all_fields = []
            for field in table_object._meta.fields:
                if not isinstance(field, AutoField):
                    all_fields.append(field.attname)

            path = BASE_DIR_LOCAL / f"data/database_tables/{table_name}.csv"

            with open(path, encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # skip the header

                for row in reader:
                    insert_dict = {}
                    row_num = 0

                    # For cvs files with varying column numbers
                    for field in all_fields:
                        row_num = row_num + 1
                        if field != "created_at" and field != "updated_at":
                            insert_dict[field] = row[row_num]

                    _, created = table_object.objects.get_or_create(**insert_dict)

            print(f"{table_name} Import Completed with {row_num} rows imported")
            results_list.append(f"{table_name}; Created: {str(row_num)}")

        return "-".join(results_list)
