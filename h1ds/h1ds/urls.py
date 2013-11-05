"""Base URLs for H1DS project.

This module provides a small number of urls, and forwards app-specific
URLS to the relevant apps.

URLS provided by this module:

* '^robots\.txt$' -- tell web-crawlers (Google et al.) which which areas to leave alone.
* '^admin/doc/'   -- docs for admin interface
* '^admin/'       -- admin interface
* '^openid/'      -- OpenID authentication

URLS passed to other H1DS modules.

* '' -- all queries are first checked against h1ds for a match.

For   the  optional   submodules  (i.e.   h1ds_mdsplus,  h1ds_summary,
h1ds_configdb),  settings.INSTALLED_APPS  is  checked to  see  if  the
submodule is installed. If  it is, then the root url  is read from the
configuration settings:

.. topic:: H1DS module root URL configuration

    The root URLS for the H1DS modules can be configured individually.

    ============= ========================== ==================
    module name   setting                    default
    ============= ========================== ==================
    h1ds_mdsplus  ``H1DS_MDSPLUS_ROOT_URL``  ``mdsplus``
    h1ds_summary  ``H1DS_SUMMARY_ROOT_URL``  ``summary``
    h1ds_configdb ``H1DS_CONFIGDB_ROOT_URL`` ``configurations``
    ============= ========================== ==================

    The  URL regular  expression used  is ``'^config_value/'``,  where
    ``config_value`` is specified by the relevant setting in the above
    table.

In the development environment  (i.e. settings.DEBUG==True), the media
files (settings.MEDIA_ROOT) are served under '^media/'

"""

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView

from h1ds import AVAILABLE_H1DS_MODULES
from h1ds.views import TextTemplateView
from h1ds.views import homepage, logout_view, edit_profile
from h1ds.views import UserMainView, WorksheetView

from h1ds.views import ApplyFilterView, UpdateFilterView, RemoveFilterView
from h1ds.views import UserSignalCreateView, UserSignalDeleteView
from h1ds.views import UserSignalUpdateView, ShotStreamView
from h1ds.views import AJAXShotRequestURL, AJAXLatestShotView, NodeView
from h1ds.views import RequestShotView, request_url, ShotDetailView
from h1ds.views import DeviceListView, DeviceDetailView, ShotListView, TreeDetailView


admin.autodiscover()


def module_urlpattern(module_name):
    mod = __import__(module_name)
    mod_url_re = r'^{}/'.format(mod.MODULE_ROOT_URL)
    mod_url_target = include('{}.urls'.format(module_name))
    return patterns('', (mod_url_re, mod_url_target))


h1ds_mods = [m for m in AVAILABLE_H1DS_MODULES if m in settings.INSTALLED_APPS]

if hasattr(settings, "H1DS_DATA_PREFIX"):
    DATA_PREFIX = settings.H1DS_DATA_PREFIX
else:
    DATA_PREFIX = "data"

core_urlpatterns = patterns('',
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
                               url(r'^create/$', UserSignalCreateView.as_view(), name="h1ds-create-user-signal"),
                               url(r'^delete/(?P<pk>\d+)$', UserSignalDeleteView.as_view(),
                                   name="h1ds-delete-user-signal"),
                               url(r'^update/(?P<pk>\d+)$', UserSignalUpdateView.as_view(),
                                   name="h1ds-update-user-signal"),
)

internal_patterns = patterns('',
                             url(r'^filter/', include(filter_patterns)),
                             url(r'^usersignal/', include(usersignal_patterns)),
                             url(r'^shot_stream/$', ShotStreamView.as_view(), name="h1ds-shot-stream"),
                             url(r'^request_shot/$', RequestShotView.as_view(), name="h1ds-request-shot"),
                             url(r'^url_for_shot/$', AJAXShotRequestURL.as_view(), name="h1ds-shot-request-url"),
                             # TODO:  should  not  have separate  AJAX  views. e.g. call with ?format=json
                             url(r'^(?P<device>[-\w]+)/latest_shot/$', AJAXLatestShotView.as_view(),
                                 name="h1ds-latest-shot"),
                             url(r'^latest_shot/$', AJAXLatestShotView.as_view(),
                                 name="h1ds-latest-shot-for-default-device"),
                             url(r'^request_url/$', request_url, name="h1ds-request-url"),
)

## Data modules
data_patterns = patterns('',
                         url(r'^$', DeviceListView.as_view(), name="device-list"),
                         url(r'^(?P<slug>[-\w]+)/$', DeviceDetailView.as_view(), name="device-detail"),
                         url(r'^(?P<slug>[-\w]+)/shots/$', ShotListView.as_view(), name="device-shot-list"),
                         url(r'^(?P<device>[-\w]+)/(?P<shot>\d+|latest)/$', ShotDetailView.as_view(),
                             name="shot-detail"),
                         url(r'^(?P<device>[-\w]+)/(?P<shot>\d+|latest)/(?P<tree>[-\w]+)/$', TreeDetailView.as_view(),
                             name="tree-detail"),

                         url(r'^(?P<device>[-\w]+)/(?P<shot>\d+|latest)/(?P<tree>[-\w]+)/(?P<nodepath>.+)/$', NodeView.as_view(),
                             name="node-detail"),
)

core_urlpatterns += patterns('',
                             url(r'^_/', include(internal_patterns)),
                             url(r'^u/', include(user_patterns)),
                             url(r'^{}/'.format(DATA_PREFIX), include(data_patterns)),
)

urlpatterns = patterns('',
                       (r'^robots\.txt$',
                        TextTemplateView.as_view(template_name='robots.txt')
                       ),
                       (r'', include(core_urlpatterns)),
                       (r'^admin/doc/',
                        include('django.contrib.admindocs.urls')),
                       (r'^admin/', include(admin.site.urls)),
                       (r'^openid/', include('django_openid_auth.urls')),
)

for mod_name in h1ds_mods:
    urlpatterns += module_urlpattern(mod_name)

if settings.DEBUG:
    urlpatterns += patterns('',
                            url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                                'document_root': settings.MEDIA_ROOT,
                            }
                            ),
    )

    
handler404 = TemplateView.as_view(template_name="errors/404.html")
handler500 = TemplateView.as_view(template_name="errors/500.html")
handler403 = TemplateView.as_view(template_name="errors/403.html")
# coming in django 1.6
# handler400 = TemplateView.as_view(template_name="400.html")
