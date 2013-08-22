from django.conf.urls.defaults import *

from h1ds_core.views import homepage, logout_view, edit_profile
from h1ds_core.views import UserMainView, WorksheetView
from django.views.decorators.cache import cache_page
from django.conf import settings

from h1ds_core.views import ApplyFilterView, UpdateFilterView, RemoveFilterView
from h1ds_core.views import UserSignalCreateView, UserSignalDeleteView
from h1ds_core.views import UserSignalUpdateView, ShotStreamView
from h1ds_core.views import AJAXShotRequestURL, AJAXLatestShotView, NodeView
from h1ds_core.views import RequestShotView, request_url, ShotListView, ShotDetailView

if hasattr(settings, "H1DS_DATA_PREFIX"):
    DATA_PREFIX = settings.H1DS_DATA_PREFIX
else:
    DATA_PREFIX = "data"


urlpatterns = patterns('',
    url(r'^$', homepage, name="h1ds-core-homepage"),
    url(r'^user/settings/(?P<username>\w+)/$', edit_profile, name="h1ds-core-edit-settings"),
    url(r'^logout/$', logout_view, name="h1ds-logout"),
)

user_patterns = patterns('',
    url(r'^(?P<username>[-\w]+)/$',
        UserMainView.as_view(),
        name="h1ds-user-main-page"),
    url(r'^(?P<username>[-\w]+)/(?P<worksheet>[-\w]+)/$',
        WorksheetView.as_view(),
        name="h1ds-user-worksheet"),
)


# Internal use

filter_patterns = patterns('',
    url(r'^apply/$', ApplyFilterView.as_view(), name="apply-filter"),
    url(r'^update/$', UpdateFilterView.as_view(), name="update-filter"),
    url(r'^remove/$', RemoveFilterView.as_view(), name="remove-filter"),
    )

usersignal_patterns = patterns('',
    url(r'^add/$', UserSignalCreateView.as_view(), name="h1ds-add-user-signal"),
    url(r'^delete/(?P<pk>\d+)$', UserSignalDeleteView.as_view(), name="h1ds-delete-user-signal"),
    url(r'^update/(?P<pk>\d+)$', UserSignalUpdateView.as_view(), name="h1ds-update-user-signal"),
    )

internal_patterns =  patterns('',
    url(r'^filter/', include(filter_patterns)),
    url(r'^usersignal/', include(usersignal_patterns)),
    url(r'^shot_stream/$', ShotStreamView.as_view(), name="h1ds-shot-stream"),
    url(r'^request_shot/$', RequestShotView.as_view(), name="h1ds-request-shot"),
    url(r'^url_for_shot/$', AJAXShotRequestURL.as_view(), name="h1ds-shot-request-url"),
    # TODO:  should  not  have separate  AJAX  views. e.g. call with ?format=json
    url(r'^latest_shot/$', AJAXLatestShotView.as_view(), name="h1ds-latest-shot-for-default-tree"),
    url(r'^latest_shot/(?P<tree_name>[^/]+)/$', AJAXLatestShotView.as_view(), name="h1ds-latest-shot"),
    url(r'^request_url/$', request_url, name="h1ds-request-url"),
    )

## Data modules
data_patterns = patterns('',
    url(r'^$', ShotListView.as_view(), name="shot-list"),
    url(r'^(?P<shot>\d+)/$', ShotDetailView.as_view(), name="shot-detail"),
    url(r'^(?P<shot>\d+)/(?P<nodepath>.+)/$', NodeView.as_view(), name="node-detail"),
    )

urlpatterns += patterns('',
    url(r'^_/', include(internal_patterns)),
    url(r'^u/', include(user_patterns)),
    url(r'^{}/'.format(DATA_PREFIX), include(data_patterns)),
    )
