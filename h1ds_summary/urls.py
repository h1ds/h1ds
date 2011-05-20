from django.conf.urls.defaults import *

from views import overview, latest_shot, ajax_latest_shot, raw_sql, add_summaryattribute

urlpatterns = patterns('',
                       url(r'^$', overview, name="h1ds-summary-homepage"),
                       url(r'^add/$', add_summaryattribute, name="add-summary-attribute"),
                       url(r'^latest_shot/$', latest_shot, name="latestshot"),
                       url(r'^ajax_latest_shot/$', ajax_latest_shot, name="ajaxlatestshot"),
                       url(r'^raw_sql/$', raw_sql, name="raw-sql"),
                       url(r'^(?P<shot_regex>[^/]+)/$', overview, name="shotoverview"),
                       url(r'^(?P<shot_regex>[^/]+)/(?P<data_regex>[^/]+)/$', overview, name="sdsummary"),
                       url(r'^(?P<shot_regex>[^/]+)/(?P<data_regex>[^/]+)/(?P<filter_regex>[^/]+)/$', overview, name="sdfsummary"),
)
