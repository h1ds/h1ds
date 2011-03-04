from django.conf.urls.defaults import *

from h1ds_core.views import homepage

urlpatterns = patterns('',
                       url(r'^$', homepage, name="h1ds-core-homepage"),
)
