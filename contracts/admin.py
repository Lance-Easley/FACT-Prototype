from django.contrib import admin
from .models import Contract
from import_export.admin import ImportExportModelAdmin

# Register your models here.
# admin.site.register(Contract)

@admin.register(Contract)
class ViewAdmin(ImportExportModelAdmin):
    pass