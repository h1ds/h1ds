from django.conf.urls.defaults import *

from h1ds_configdb.views import configdb_home, config_overview

urlpatterns = patterns('',
                       url(r'^$', configdb_home, name="h1ds-configdb-homepage"),
                       url(r'^(?P<config_id>.*)/$', config_overview, name="configdb_overview"),
                       
)
