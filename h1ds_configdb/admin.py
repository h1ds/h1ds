from django.contrib import admin
from h1ds_configdb.models import ConfigDBFileType, ConfigDBFile, ConfigDBProperty, ConfigDBPropertyType, ConfigDBStringProperty, ConfigDBFloatProperty, ConfigDBIntProperty
from django.contrib.admin.actions import delete_selected


class ConfigDBPropertyAdmin(admin.ModelAdmin):
    list_display = ['configdb_file', 'configdb_propertytype', 'value']
    actions = [delete_selected]
admin.site.register(ConfigDBProperty, ConfigDBPropertyAdmin)

class ConfigDBStringPropertyAdmin(admin.ModelAdmin):
    list_display = ['value',]
    actions = [delete_selected]
admin.site.register(ConfigDBStringProperty, ConfigDBStringPropertyAdmin)

class ConfigDBFloatPropertyAdmin(admin.ModelAdmin):
    list_display = ['value',]
    actions = [delete_selected]
admin.site.register(ConfigDBFloatProperty, ConfigDBFloatPropertyAdmin)

class ConfigDBIntPropertyAdmin(admin.ModelAdmin):
    list_display = ['value',]
    actions = [delete_selected]
admin.site.register(ConfigDBIntProperty, ConfigDBIntPropertyAdmin)


class ConfigDBFileTypeAdmin(admin.ModelAdmin):
    list_display = ['name',]
    actions = [delete_selected]
admin.site.register(ConfigDBFileType, ConfigDBFileTypeAdmin)

class ConfigDBFileAdmin(admin.ModelAdmin):
    list_display = ['dbfile',]
    actions = [delete_selected]
admin.site.register(ConfigDBFile, ConfigDBFileAdmin)

class ConfigDBPropertyTypeAdmin(admin.ModelAdmin):
    list_display = ['name',]
    actions = [delete_selected]
admin.site.register(ConfigDBPropertyType, ConfigDBPropertyTypeAdmin)
