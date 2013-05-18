from django.conf.urls.defaults import *

from h1ds_core.views import homepage, logout_view, edit_profile
from h1ds_core.views import UserMainView, WorksheetView
from django.views.decorators.cache import cache_page
from django.conf import settings

from h1ds_core.views import ApplyFilterView, UpdateFilterView, RemoveFilterView
from h1ds_core.views import UserSignalCreateView, UserSignalDeleteView
from h1ds_core.views import UserSignalUpdateView, ShotStreamView
from h1ds_core.views import AJAXShotRequestURL, AJAXLatestShotView, NodeView
from h1ds_core.views import RequestShotView, request_url

urlpatterns = patterns('',
                       url(r'^$',
                           homepage,
                           name="h1ds-core-homepage"),
                       url(r'^user/settings/(?P<username>\w+)/$',
                           edit_profile,
                           name="h1ds-core-edit-settings"),
                       url(r'^logout/$',
                           logout_view,
                           name="h1ds-logout"),
                       url(r'^u/(?P<username>[-\w]+)/$',
                           UserMainView.as_view(),
                           name="h1ds-user-main-page"),
                       url(r'^u/(?P<username>[-\w]+)/(?P<worksheet>[-\w]+)/$',
                           WorksheetView.as_view(),
                           name="h1ds-user-worksheet"),
                       
)

# Internal use
urlpatterns += patterns('',
                       url(r'^_/filter/apply$',
                           ApplyFilterView.as_view(),
                           name="apply-filter"),
                       url(r'^_/filter/update$',
                           UpdateFilterView.as_view(),
                           name="update-filter"),
                       url(r'^_/filter/remove$',
                           RemoveFilterView.as_view(),
                           name="remove-filter"),
                       url(r'^_/usersignal/add$',
                           UserSignalCreateView.as_view(),
                           name="h1ds-add-user-signal"),
                       url(r'^_/usersignal/delete/(?P<pk>\d+)$',
                           UserSignalDeleteView.as_view(),
                           name="h1ds-delete-user-signal"),
                       url(r'^_/usersignal/update/(?P<pk>\d+)$',
                           UserSignalUpdateView.as_view(),
                           name="h1ds-update-user-signal"),
                       url(r'^_/shot_stream/$',
                           ShotStreamView.as_view(),
                           name="h1ds-shot-stream"),
                       url(r'^_/request_shot$',
                           RequestShotView.as_view(),
                           name="h1ds-request-shot"),
                       url(r'^_/url_for_shot$',
                           AJAXShotRequestURL.as_view(),
                           name="h1ds-shot-request-url"),
                       # TODO:  should  not  have separate  AJAX  views.
                       # e.g. call with ?format=json
                       url(r'^_/latest_shot/$',
                           AJAXLatestShotView.as_view(),
                           name="h1ds-latest-shot-for-default-tree"),
                       url(r'^_/latest_shot/(?P<tree_name>[^/]+)/$',
                           AJAXLatestShotView.as_view(),
                           name="h1ds-latest-shot"),
                       url(r'^_/request_url$',
                           request_url,
                           name="h1ds-request-url"),
    )

## Data modules
data_prefix = r"^"
if hasattr(settings, "H1DS_DATA_PREFIX"):
    data_prefix = r'^{}'.format(settings.H1DS_DATA_PREFIX)

#urlpatterns += patterns('',
#                        url(data_prefix+"(?P<url>.+)$",
#                             cache_page(60*30)(NodeView.as_view()),
#                             name="h1ds-node"))
urlpatterns += patterns('',
                        url(data_prefix+"/(?P<nodepath>.+)/$",
                             NodeView.as_view(),
                             name="node-detail"))

