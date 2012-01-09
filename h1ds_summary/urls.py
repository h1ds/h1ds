from django.conf.urls.defaults import *

from h1ds_summary.views import raw_sql, get_summary_attribute_form_from_url, go_to_source
from h1ds_summary.views import SummaryView, AddSummaryAttribiteView, RecomputeSummaryView


urlpatterns = patterns('',
                       url(r'^_/get_summary_attribute_form_from_url/$', 
                           get_summary_attribute_form_from_url, 
                           name="get-summary-attribute-form-from-url"),
                       url(r'^_/add/$', 
                           AddSummaryAttribiteView.as_view(), 
                           name="add-summary-attribute"),
                       url(r'^_/go_to_source/(?P<slug>[^/]+)/(?P<shot>\d+)/$', 
                           go_to_source, name="summary-go-to-source"),
                       url(r'^_/raw_sql/$', raw_sql, name="raw-sql"),
                       )

urlpatterns += patterns('',
                       url(r'^$', SummaryView.as_view(), name="h1ds-summary-homepage"),
                       url(r'^(?P<shot_str>[^/]+)/$', SummaryView.as_view(), name="shotoverview"),
                       url(r'^(?P<shot_str>[^/]+)/(?P<attr_str>[^/]+)/$', SummaryView.as_view(), name="sdsummary"),
                       url(r'^(?P<shot_str>[^/]+)/(?P<attr_str>[^/]+)/(?P<filter_str>[^/]+)/$', SummaryView.as_view(), name="sdfsummary"),
)
