from django.conf.urls.defaults import *

from views import overview

urlpatterns = patterns('',
                       url(r'^$', overview, name="summaryoverview"),
                       url(r'^(?P<shot_regex>[^/]+)/$', overview, name="shotoverview"),
                       url(r'^(?P<shot_regex>[^/]+)/(?P<data_regex>[^/]+)/$', overview, name="sdsummary"),
                       url(r'^(?P<shot_regex>[^/]+)/(?P<data_regex>[^/]+)/(?P<filter_regex>[^/]+)/$', overview, name="sdfsummary"),
)
