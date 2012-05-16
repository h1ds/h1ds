from django.conf.urls.defaults import *

#from h1ds_configdb.views import configdb_home, config_overview
from h1ds_configdb.views import HomeView

urlpatterns = patterns('',
                       url(r'^$', HomeView.as_view(), name="h1ds-configdb-homepage"),
                       #url(r'^(?P<config_id>.*)/$', config_overview, name="configdb_overview"),
                       
)
