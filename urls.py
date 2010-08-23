from django.conf.urls.defaults import *

from views import summary_overview, shot_overview, shot_data_overview, shot_data_filter_overview

urlpatterns = patterns('',
                       url(r'^$', summary_overview, name="summaryoverview"),
                       url(r'^(?P<shot_regex>[^/]+)/$', shot_overview, name="shotoverview"),
                       url(r'^(?P<shot_regex>[^/]+)/(?P<data_regex>[^/]+)/$', shot_data_overview, name="sdsummary"),
                       url(r'^(?P<shot_regex>[^/]+)/(?P<data_regex>[^/]+)/(?P<filter_regex>[^/]+)/$', shot_data_filter_overview, name="sdfsummary"),
)
