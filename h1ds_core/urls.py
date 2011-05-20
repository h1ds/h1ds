from django.conf.urls.defaults import *

from h1ds_core.views import homepage, dashboard, logout_view

urlpatterns = patterns('',
                       url(r'^$', homepage, name="h1ds-core-homepage"),
                       url(r'^logout/$', logout_view, name="h1ds-logout"),
                       url(r'^dashboard/$', dashboard, name="h1ds-core-dashboard"),
)
