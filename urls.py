from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
                       (r'^robots\.txt$', direct_to_template,
                        {'template': 'robots.txt', 'mimetype': 'text/plain'}),
                       (r'', include('h1ds_core.urls')),
                       (r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       (r'^admin/', include(admin.site.urls)),
                       (r'^openid/', include('django_openid_auth.urls')),
                       (r'^mdsplus/', include('h1ds_mdsplus.urls')),
                       (r'^summary/', include('h1ds_summary.urls')),
                       (r'^configurations/', include('h1ds_configdb.urls')),
                       (r'^docs/', include('sphinxdoc.urls')),
                       (r'^search/', include('haystack.urls')),
                       )

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                'document_root': settings.MEDIA_ROOT,
                }
            ),
    )
