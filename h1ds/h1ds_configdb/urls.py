from django.conf.urls.defaults import *

from h1ds_configdb.views import HomeView

from django.utils.functional import lazy
from django.core.urlresolvers import reverse
from django.views.generic import RedirectView

# TODO: when update to django 1.4, use inbuilt reverse_lazy
reverse_lazy = lazy(reverse, str)

urlpatterns = patterns('',
                       url(r'^$',
                           RedirectView.as_view(
                               url=reverse_lazy("h1ds-configdb-filetypes", kwargs={'filetype_str': 'all_filetypes'})),
                           name="h1ds-configdb-homepage"),
                       url(r'^(?P<filetype_str>[^/]+)/$',
                           HomeView.as_view(), name="h1ds-configdb-filetypes"),
                       url(r'^(?P<filetype_str>[^/]+)/(?P<filter_str>[^/]+)/$',
                           HomeView.as_view(), name="h1ds-configdb-filtered")
)

