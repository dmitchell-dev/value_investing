from django.db import models

from api_import.managers import ImportRecordQueryset


class ImportRecord(models.Model):
    symbol = models.CharField(max_length=255)
    import_type = models.CharField(max_length=255)
    fetchtime = models.DateTimeField(blank=True, null=True)

    objects = ImportRecordQueryset.as_manager()

    class Meta:
        db_table = "import_record"
        verbose_name = "Import Record"
        verbose_name_plural = "Import Records"

    def __str__(self):
        return str(self.fetchtime)
