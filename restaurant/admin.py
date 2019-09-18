from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import (
    Dish
)

from import_export.admin import ImportExportModelAdmin

@admin.register(Dish)
class DishAdmin(ImportExportModelAdmin):
    list_display = ('name', 'price', 'category')
    list_filter = ('category', 'price')