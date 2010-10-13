from django.conf.urls.defaults import *

from views import overview, latest_shot, ajax_latest_shot

urlpatterns = patterns('',
                       url(r'^$', overview, name="summaryoverview"),
                       url(r'^latest_shot/$', latest_shot, name="latestshot"),
                       url(r'^ajax_latest_shot/$', ajax_latest_shot, name="ajaxlatestshot"),
                       url(r'^(?P<shot_regex>[^/]+)/$', overview, name="shotoverview"),
                       url(r'^(?P<shot_regex>[^/]+)/(?P<data_regex>[^/]+)/$', overview, name="sdsummary"),
                       url(r'^(?P<shot_regex>[^/]+)/(?P<data_regex>[^/]+)/(?P<filter_regex>[^/]+)/$', overview, name="sdfsummary"),
)
