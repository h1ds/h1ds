from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       (r'', include('h1ds_core.urls')),
                       (r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       (r'^admin/', include(admin.site.urls)),
                       (r'^openid/', include('django_openid_auth.urls')),
                       (r'^mdsplus/', include('h1ds_mdsplus.urls')),
                       (r'^summary/', include('h1ds_summary.urls')),
                       (r'^configurations/', include('h1ds_configdb.urls')),
                       )

