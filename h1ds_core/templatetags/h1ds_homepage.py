from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
register = template.Library()

item_template = (
'<div class="mbox">'
    '<h2>'
        '<a href="%(url)s">%(name)s</a>'
    '</h2>'
    '<p>%(description)s</p>'
'</div>'
)

H1DS_APP_BLACKLIST = ['h1ds_core', settings.H1DS_DATA_MODULE]

class H1DSHomepageNode(template.Node):
    def render(self, context):
        h1ds_installed_apps = []
        for app in settings.INSTALLED_APPS:
            if app.startswith("h1ds_") and not app in H1DS_APP_BLACKLIST:
                h1ds_installed_apps.append(app)
        
        # TODO: don't hardcode this stuff
        tag_string = item_template %{"url":"/data",
                                     "name":"Data",
                                     "description":"Data viewer"}
        
        
        for app in h1ds_installed_apps:
            homepage_url_name = app.replace('_', '-')+'-homepage'
            homepage_url = reverse(homepage_url_name)
            version_module = '.'.join([app, 'version'])
            app_module =  __import__(version_module, globals(), locals(), [])
            app_doc_name = app_module.MODULE_DOC_NAME
            app_description = app_module.__doc__

            tag_string += (item_template %{'url':homepage_url,
                                           'name':app_doc_name,
                                           'description':app_description})
        if hasattr(settings, 'H1DS_EXTRA_SUBLINKS'):
            for link in settings.H1DS_EXTRA_SUBLINKS:
                tag_string += (item_template %{'url':link[1],
                                               'name':link[0],
                                               'description':link[2]})
        return tag_string

def do_h1ds_homepage(parser, token):
    """Populate H1DS homepage links to registered H1DS modules."""

    return H1DSHomepageNode()

register.tag('h1ds_homepage', do_h1ds_homepage)
do_h1ds_homepage.is_safe = True

