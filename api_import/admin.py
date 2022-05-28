from django.contrib import admin

from .models import ImportRecord


class ImportRecordAdmin(admin.ModelAdmin):
    fields = ["symbol"]


admin.site.register(ImportRecord, ImportRecordAdmin)
