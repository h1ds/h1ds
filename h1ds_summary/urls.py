from django.conf.urls.defaults import *

from h1ds_summary.views import raw_sql, get_summary_attribute_form_from_url, go_to_source
from h1ds_summary.views import SummaryView, AddSummaryAttribiteView

urlpatterns = patterns('',
                       url(r'^$', SummaryView.as_view(), name="h1ds-summary-homepage"),
                       url(r'^get_summary_attribute_form_from_url/$', get_summary_attribute_form_from_url, name="get-summary-attribute-form-from-url"),
                       url(r'^add/$', AddSummaryAttribiteView.as_view(), name="add-summary-attribute"),
                       url(r'^go_to_source/(?P<slug>[^/]+)/(?P<shot>\d+)/$', go_to_source, name="summary-go-to-source"),
                       url(r'^raw_sql/$', raw_sql, name="raw-sql"),
                       url(r'^(?P<shot_str>[^/]+)/$', SummaryView.as_view(), name="shotoverview"),
                       url(r'^(?P<shot_str>[^/]+)/(?P<attr_str>[^/]+)/$', SummaryView.as_view(), name="sdsummary"),
                       url(r'^(?P<shot_str>[^/]+)/(?P<attr_str>[^/]+)/(?P<filter_str>[^/]+)/$', SummaryView.as_view(), name="sdfsummary"),
)
