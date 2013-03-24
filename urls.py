"""Base URLs for H1DS project.

This module provides a small number of urls, and forwards app-specific
URLS to the relevant apps.

URLS provided by this module:

* '^robots\.txt$' -- tell web-crawlers (Google et al.) which which areas to leave alone.
* '^admin/doc/'   -- docs for admin interface
* '^admin/'       -- admin interface
* '^openid/'      -- OpenID authentication

URLS passed to other H1DS modules.

* '' -- all queries are first checked against h1ds_core for a match.

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
import sys

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings

from h1ds import AVAILABLE_H1DS_MODULES
from h1ds.views import TextTemplateView



admin.autodiscover()

def module_urlpattern(mod_name):
    mod = __import__(mod_name)
    mod_url_re = r'^{}/'.format(mod.MODULE_ROOT_URL)
    mod_url_target = include('{}.urls'.format(mod_name))
    return patterns('', (mod_url_re, mod_url_target))


h1ds_mods = [m for m in AVAILABLE_H1DS_MODULES if (m in settings.INSTALLED_APPS and m != settings.H1DS_DATA_MODULE)]

urlpatterns = patterns('',
                       (r'^robots\.txt$', 
                        TextTemplateView.as_view(template_name='robots.txt')
                        ),
                       (r'', include('h1ds_core.urls')),
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
