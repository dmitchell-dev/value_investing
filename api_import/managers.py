from django.db.models import QuerySet


class ImportRecordQueryset(QuerySet):
    def get_import_record(self):
        return self.values(
            "id",
            "symbol",
            "import_type",
            "fetchtime",
        )
