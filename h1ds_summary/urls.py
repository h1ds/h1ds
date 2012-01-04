from django.conf.urls.defaults import *

from h1ds_summary.views import latest_shot, ajax_latest_shot, raw_sql, add_summary_attribute, get_summary_attribute_form_from_url, go_to_source
from h1ds_summary.views import SummaryView

urlpatterns = patterns('',
                       url(r'^$', SummaryView.as_view(), name="h1ds-summary-homepage"),
                       url(r'^get_summary_attribute_form_from_url/$', get_summary_attribute_form_from_url, name="get-summary-attribute-form-from-url"),
                       url(r'^add/$', add_summary_attribute, name="add-summary-attribute"),
                       url(r'^go_to_source/(?P<slug>[^/]+)/(?P<shot>\d+)/$', go_to_source, name="summary-go-to-source"),
                       url(r'^latest_shot/$', latest_shot, name="latestshot"),
                       url(r'^ajax_latest_shot/$', ajax_latest_shot, name="ajaxlatestshot"),
                       url(r'^raw_sql/$', raw_sql, name="raw-sql"),
                       url(r'^(?P<shot_str>[^/]+)/$', SummaryView.as_view(), name="shotoverview"),
                       url(r'^(?P<shot_str>[^/]+)/(?P<attr_str>[^/]+)/$', SummaryView.as_view(), name="sdsummary"),
                       url(r'^(?P<shot_str>[^/]+)/(?P<attr_str>[^/]+)/(?P<filter_str>[^/]+)/$', SummaryView.as_view(), name="sdfsummary"),
)
