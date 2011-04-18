from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
register = template.Library()

item_template = '<div class="item"><a class="item-link" href="%(url)s">%(name)s</a><p>%(description)s</p></div>'

class H1DSHomepageNode(template.Node):
    def render(self, context):
        h1ds_installed_apps = [a for a in settings.INSTALLED_APPS if a.startswith('h1ds_') and a != 'h1ds_core']
        
        tag_string = ""
        for app in h1ds_installed_apps:
            homepage_url_name = app.replace('_', '-')+'-homepage'
            homepage_url = reverse(homepage_url_name)
            app_module =  __import__('.'.join([app, 'version']), globals(), locals(), [])
            app_doc_name = app_module.MODULE_DOC_NAME
            app_description = app_module.__doc__

            tag_string += (item_template %{'url':homepage_url, 'name':app_doc_name, 'description':app_description})
        return tag_string

def do_h1ds_homepage(parser, token):
    return H1DSHomepageNode()

register.tag('h1ds_homepage', do_h1ds_homepage)
do_h1ds_homepage.is_safe = True

