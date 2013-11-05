from django.conf.urls import *

from h1ds_summary.views import get_summary_attribute_form_from_url, go_to_source
from h1ds_summary.views import SummaryView, AddSummaryAttribiteView, RecomputeSummaryView
from h1ds_summary.views import AJAXLatestSummaryShotView, AJAXLastUpdateTimeView, SummaryDeviceListView
from h1ds_summary.views import RawSQLView, ControlPanelView

internal_patterns = patterns('',
                             url(r'^get_summary_attribute_form_from_url/$',
                                 get_summary_attribute_form_from_url,
                                 name="get-summary-attribute-form-from-url"),
                             url(r'^raw_sql/$', RawSQLView.as_view(), name="raw-sql"),
                             )

device_internal_patterns = patterns('',
                                    url(r'^add/$',
                                    AddSummaryAttribiteView.as_view(),
                                    name="add-summary-attribute"),
                                    url(r'^go_to_source/(?P<slug>[^/]+)/(?P<shot>\d+)/$',
                                    go_to_source, name="summary-go-to-source"),
                                    url(r'^get_latest_summarydb_shot/$',
                                    AJAXLatestSummaryShotView.as_view(),
                                    name="summary-get-latest-shot"),
                                    url(r'^get_last_update_time/$',
                                    AJAXLastUpdateTimeView.as_view(),
                                    name="summary-get-last-update-time"),
                                    url(r'^recompute/$',
                                    RecomputeSummaryView.as_view(), name="summary-recompute"),
                                    )

device_summary_patterns = patterns('',
                                   url(r'^$',
                                       SummaryView.as_view(), name="h1ds-summary-device-homepage"),
                                   url('^control_panel/$', ControlPanelView.as_view(), name='summary-control-panel'),
                                   (r'^_/', include(device_internal_patterns)),
                                   url(r'^(?P<shot_str>[^/]+)/$',
                                       SummaryView.as_view(), name="shotoverview"),
                                   url(r'^(?P<shot_str>[^/]+)/(?P<attr_str>[^/]+)/$',
                                       SummaryView.as_view(), name="sdsummary"),
                                   url(r'^(?P<shot_str>[^/]+)/(?P<attr_str>[^/]+)/(?P<filter_str>[^/]+)/$',
                                       SummaryView.as_view(), name="sdfsummary"),
                                   )
urlpatterns = patterns('',
                       url(r'^$', SummaryDeviceListView.as_view(), name='h1ds-summary-homepage'),
                       (r'^_/', include(internal_patterns)),
                       (r'^(?P<device>[-\w]+)/', include(device_summary_patterns))
                       )