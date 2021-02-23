from django.contrib import admin
from .models import Container
from import_export.admin import ImportExportModelAdmin

# Register your models here.
# admin.site.register(Container)

@admin.register(Container)
class ViewAdmin(ImportExportModelAdmin):
    pass