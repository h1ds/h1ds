from django.contrib import admin
from h1ds_core.models import H1DSSignal, H1DSSignalInstance, Worksheet
from h1ds_core.models import UserSignal

class H1DSSignalAdmin(admin.ModelAdmin):
    pass

admin.site.register(H1DSSignal, H1DSSignalAdmin)

class H1DSSignalInstanceAdmin(admin.ModelAdmin):
    pass

admin.site.register(H1DSSignalInstance, H1DSSignalInstanceAdmin)

class WorksheetAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(Worksheet, WorksheetAdmin)


class UserSignalAdmin(admin.ModelAdmin):
    pass

admin.site.register(UserSignal, UserSignalAdmin)

