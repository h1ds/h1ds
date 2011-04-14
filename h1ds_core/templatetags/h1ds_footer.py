from django import template
from django.conf import settings
register = template.Library()

class H1DSFooterNode(template.Node):
    def render(self, context):
        h1ds_installed_apps = [a for a in settings.INSTALLED_APPS if a.startswith('h1ds_')]
        app_strings = []
        for app in h1ds_installed_apps:
            try:
                app_module =  __import__('.'.join([app, 'version']), globals(), locals(), [])
                app_strings.append("%s (%s)" %(app, app_module.version.get_version()))
            except:
                app_strings.append(app)
        return " &middot; ".join(app_strings)


def do_h1ds_footer(parser, token):
    return H1DSFooterNode()

register.tag('h1ds_footer', do_h1ds_footer)
