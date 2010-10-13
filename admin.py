from django.contrib import admin
from h1ds_summary.models import SummaryAttribute, Shot, FloatAttributeInstance, IntegerAttributeInstance, DateTimeAttributeInstance
from h1ds_summary.tasks import update_attribute

admin.site.disable_action('delete_selected')

def reload_attribute(modeladmin, request, queryset):
    shots = Shot.objects.all()
    for summary_attribute in queryset:
        # delete any existing instances of the attribute
        summary_attribute.delete_instances()
        # update for all shots
        for s in shots:
            result = update_attribute.delay(s,summary_attribute)
            #new_attr = summary_attribute.get_att_class()()
            #new_attr.shot = s
            #new_attr.attribute = summary_attribute
            #new_attr.value = summary_attribute.get_value(s.shot)
            #new_attr.save()

        
reload_attribute.short_description = "Reload attribute for all shots in summary database."

class SummaryAttributeAdmin(admin.ModelAdmin):
    actions = [reload_attribute]
    list_display = ('slug', 'name', 'is_default', 'data_type', 'default_min', 'default_max', 'display_format', 'source')
    list_display_links = ('slug',)
    list_editable = ('name', 'data_type', 'is_default', 'default_min', 'default_max', 'display_format', 'source')
admin.site.register(SummaryAttribute, SummaryAttributeAdmin)

class ShotAdmin(admin.ModelAdmin):
    pass
admin.site.register(Shot, ShotAdmin)

class FloatAttributeInstanceAdmin(admin.ModelAdmin):
    pass
admin.site.register(FloatAttributeInstance, FloatAttributeInstanceAdmin)


class IntegerAttributeInstanceAdmin(admin.ModelAdmin):
    pass
admin.site.register(IntegerAttributeInstance, IntegerAttributeInstanceAdmin)

class DateTimeAttributeInstanceAdmin(admin.ModelAdmin):
    pass
admin.site.register(DateTimeAttributeInstance, DateTimeAttributeInstanceAdmin)

