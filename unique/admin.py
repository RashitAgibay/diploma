from django.contrib import admin
from unique.models import City, UniqueSys, GoalOfSupport
from import_export.admin import ImportExportModelAdmin

admin.site.register([UniqueSys, GoalOfSupport])


@admin.register(City)
class ViewAdmin(ImportExportModelAdmin):
    pass
