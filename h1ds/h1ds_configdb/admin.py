import os
from django.contrib import admin
from django.contrib.admin.actions import delete_selected
from django import forms

from h1ds_configdb.models import ConfigDBFileType, ConfigDBFile, ConfigDBProperty, ConfigDBPropertyType, ConfigDBLoadingDir
from h1ds_configdb.utils import scan_configdb_dir


class ConfigDBLoadingDirAdminForm(forms.ModelForm):
    class Meta:
        model = ConfigDBLoadingDir

    def clean_folder(self):
        folder = self.cleaned_data["folder"]
        if not os.path.exists(folder):
            raise forms.ValidationError("Folder %s doesn't exist on the server." % folder)
        return folder


class ConfigDBLoadingDirAdmin(admin.ModelAdmin):
    form = ConfigDBLoadingDirAdminForm

    actions = ['scan_dir']

    def scan_dir(self, request, queryset):
        for d in queryset.all():
            scan_configdb_dir(d.folder, d.force_overwrite)

    scan_dir.short_description = "Scan selected directories"


admin.site.register(ConfigDBLoadingDir, ConfigDBLoadingDirAdmin)


class ConfigDBPropertyAdmin(admin.ModelAdmin):
    list_display = ['configdb_file', 'configdb_propertytype', 'value_float', 'value_integer']
    actions = [delete_selected]


admin.site.register(ConfigDBProperty, ConfigDBPropertyAdmin)


class ConfigDBFileTypeAdmin(admin.ModelAdmin):
    list_display = ['name', ]
    actions = [delete_selected]


admin.site.register(ConfigDBFileType, ConfigDBFileTypeAdmin)


class ConfigDBFileAdmin(admin.ModelAdmin):
    list_display = ['dbfile', ]
    actions = [delete_selected]


admin.site.register(ConfigDBFile, ConfigDBFileAdmin)


class ConfigDBPropertyTypeAdmin(admin.ModelAdmin):
    list_display = ['name', ]
    actions = [delete_selected]


admin.site.register(ConfigDBPropertyType, ConfigDBPropertyTypeAdmin)
