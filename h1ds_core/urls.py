from django.conf.urls.defaults import *

from h1ds_core.views import homepage, logout_view, edit_profile
from h1ds_core.views import UserMainView, WorksheetView

urlpatterns = patterns('',
                       url(r'^$', homepage, name="h1ds-core-homepage"),
                       url(r'^user/settings/(?P<username>\w+)/$', edit_profile, name="h1ds-core-edit-settings"),
                       url(r'^logout/$', logout_view, name="h1ds-logout"),
                       url(r'^u/(?P<username>[-\w]+)/$', UserMainView.as_view(), name="h1ds-user-main-page"),
                       url(r'^u/(?P<username>[-\w]+)/(?P<worksheet>[-\w]+)/$', WorksheetView.as_view(), name="h1ds-user-worksheet"),
                       
)
