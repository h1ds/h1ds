from django.contrib import admin
from django.forms import models
from h1ds.models import H1DSSignal, H1DSSignalInstance, Worksheet, Shot
from h1ds.models import UserSignal, SubTree, Filter, FilterDtype, FilterDim, Device
from h1ds.models import Tree, Node, ShotRange, NodePath


class DeviceAdminForm(models.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DeviceAdminForm, self).__init__(*args, **kwargs)
        self.fields['latest_shot'].queryset = Shot.objects.filter(device=self.instance)


class DeviceAdmin(admin.ModelAdmin):
    form = DeviceAdminForm
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Device, DeviceAdmin)


class H1DSSignalAdmin(admin.ModelAdmin):
    pass


admin.site.register(H1DSSignal, H1DSSignalAdmin)


class NodeAdmin(admin.ModelAdmin):
    pass

admin.site.register(Node, NodeAdmin)

class NodePathAdmin(admin.ModelAdmin):
    pass

admin.site.register(NodePath, NodePathAdmin)

class TreeAdmin(admin.ModelAdmin):
    pass

admin.site.register(Tree, TreeAdmin)

class ShotRangeAdmin(admin.ModelAdmin):
    pass

admin.site.register(ShotRange, ShotRangeAdmin)

class H1DSSignalInstanceAdmin(admin.ModelAdmin):
    pass


admin.site.register(H1DSSignalInstance, H1DSSignalInstanceAdmin)


class WorksheetAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Worksheet, WorksheetAdmin)


class UserSignalAdmin(admin.ModelAdmin):
    pass


admin.site.register(UserSignal, UserSignalAdmin)


class SubTreeAdmin(admin.ModelAdmin):
    pass
    #prepopulated_fields = {"slug": ("path",)}


admin.site.register(SubTree, SubTreeAdmin)


class FilterAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Filter, FilterAdmin)


class FilterDtypeAdmin(admin.ModelAdmin):
    pass


admin.site.register(FilterDtype, FilterDtypeAdmin)


class FilterDimAdmin(admin.ModelAdmin):
    pass


admin.site.register(FilterDim, FilterDimAdmin)


class ShotAdmin(admin.ModelAdmin):
    actions = ['delete_selected']


admin.site.register(Shot, ShotAdmin)
