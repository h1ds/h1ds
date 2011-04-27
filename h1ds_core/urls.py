from django.conf.urls.defaults import *

from h1ds_core.views import homepage, dashboard

urlpatterns = patterns('',
                       url(r'^$', homepage, name="h1ds-core-homepage"),
                       url(r'^dashboard/$', dashboard, name="h1ds-core-dashboard"),
)
