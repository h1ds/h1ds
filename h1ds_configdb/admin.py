from django.contrib import admin
from h1ds_configdb.models import ConfigDBFileType, ConfigDBFile, ConfigDBPropertyType, ConfigDBBaseProperty, ConfigDBStringProperty, ConfigDBFloatProperty, ConfigDBIntProperty
from django.contrib.admin.actions import delete_selected

admin.site.register(ConfigDBBaseProperty)
admin.site.register(ConfigDBStringProperty)
admin.site.register(ConfigDBFloatProperty)
admin.site.register(ConfigDBIntProperty)

class ConfigDBFileTypeAdmin(admin.ModelAdmin):
    list_display = ['name',]
    actions = [delete_selected]
admin.site.register(ConfigDBFileType, ConfigDBFileTypeAdmin)

class ConfigDBFileAdmin(admin.ModelAdmin):
    list_display = ['filename',]
    actions = [delete_selected]
admin.site.register(ConfigDBFile, ConfigDBFileAdmin)

class ConfigDBPropertyTypeAdmin(admin.ModelAdmin):
    list_display = ['name',]
    actions = [delete_selected]
admin.site.register(ConfigDBPropertyType, ConfigDBPropertyTypeAdmin)
