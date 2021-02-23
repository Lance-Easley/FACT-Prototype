from django.contrib import admin
from .models import QueuedContract
from import_export.admin import ImportExportModelAdmin

# Register your models here.
# admin.site.register(QueuedContract)

@admin.register(QueuedContract)
class ViewAdmin(ImportExportModelAdmin):
    pass