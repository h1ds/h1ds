from django import template
from django.conf import settings
register = template.Library()

class H1DSTitleNode(template.Node):
    def render(self, context):
        try:
            return settings.H1DS_TITLE
        except:
            return ""

def do_h1ds_title(parser, token):
    return H1DSTitleNode()

class H1DSHeaderNode(template.Node):
    def render(self, context):
        try:
            subtitle_strings = " &middot; ".join(['<a href="%s">%s</a>' %(s[1],s[0]) for s in settings.H1DS_SUBLINKS])
            return_string = '<div id="title"><a href="/">%s</a>' %(settings.H1DS_TITLE)
            return_string += '<div id="subtitle">'+subtitle_strings+'</div></div>'
            return return_string
        except:
            return ""

def do_h1ds_header(parser, token):
    return H1DSHeaderNode()

class H1DSFooterNode(template.Node):
    def render(self, context):
        h1ds_installed_apps = [a for a in settings.INSTALLED_APPS if a.startswith('h1ds_')]
        app_strings = []
        for app in h1ds_installed_apps:
            try:
                app_module =  __import__('.'.join([app, 'version']), globals(), locals(), [])
                app_strings.append("%s %s" %(app, app_module.version.get_version()))
            except:
                app_strings.append(app)
        return " &middot; ".join(app_strings)

def do_h1ds_footer(parser, token):
    return H1DSFooterNode()

register.tag('h1ds_title', do_h1ds_title)
register.tag('h1ds_header', do_h1ds_header)
register.tag('h1ds_footer', do_h1ds_footer)
do_h1ds_title.is_safe = True
do_h1ds_header.is_safe = True
do_h1ds_footer.is_safe = True

