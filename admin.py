from django.contrib import admin
from h1ds_summary.models import SummaryAttribute

class SummaryAttributeAdmin(admin.ModelAdmin):
    pass
admin.site.register(SummaryAttribute, SummaryAttributeAdmin)
