from django.contrib import admin
from h1ds_summary.models import SummaryAttribute

# The   delete  selected   action   is  disabled   because  it   deletes
# SummaryAttributes but not via the delete() method, which means columns
# in  the summary  table aren't  removed. TODO:  create a  custom action
# which calls the individual delete() methods.
admin.site.disable_action('delete_selected')

class SummaryAttributeAdmin(admin.ModelAdmin):
    #actions = [reload_attribute]
    list_display = ('slug', 'name', 'is_default', 'source', 'display_order')
    list_display_links = ('slug',)
    list_editable = ('name', 'is_default', 'source', 'display_order')
admin.site.register(SummaryAttribute, SummaryAttributeAdmin)
