from django.contrib import admin
from h1ds_summary.models import SummaryAttribute


class SummaryAttributeAdmin(admin.ModelAdmin):
    #actions = [reload_attribute]
    list_display = ('slug', 'name', 'is_default', 'data_type', 'source_url', 'display_order')
    list_display_links = ('slug',)
    list_editable = ('name', 'data_type', 'is_default', 'source_url', 'display_order')
admin.site.register(SummaryAttribute, SummaryAttributeAdmin)
