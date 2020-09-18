from django.contrib import admin
from .models import ScrapedData


class ReadOnlyFields(admin.ModelAdmin):
    readonly_fields = ('created_on', 'edited_on')


admin.site.register(ScrapedData, ReadOnlyFields)
