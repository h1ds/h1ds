from django.contrib import admin
from h1ds_summary.models import SummaryAttribute, Shot, FloatAttributeInstance

def reload_attribute(modeladmin, request, queryset):
    shots = Shot.objects.all()
    for summary_attribute in queryset:
        # delete any existing instances of the attribute
        summary_attribute.delete_instances()
        # update for all shots
        for s in shots:
            new_attr = summary_attribute.get_att_class()()
            new_attr.shot = s
            new_attr.attribute = summary_attribute
            new_attr.value = summary_attribute.get_value(s.shot)
            new_attr.save()

        
reload_attribute.short_description = "Reload attribute for all shots in summary database."

class SummaryAttributeAdmin(admin.ModelAdmin):
    actions = [reload_attribute]
admin.site.register(SummaryAttribute, SummaryAttributeAdmin)

class ShotAdmin(admin.ModelAdmin):
    pass
admin.site.register(Shot, ShotAdmin)

class FloatAttributeInstanceAdmin(admin.ModelAdmin):
    pass
admin.site.register(FloatAttributeInstance, FloatAttributeInstanceAdmin)

