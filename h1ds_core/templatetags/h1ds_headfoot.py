from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

register = template.Library()

h1ds_installed_apps = [a for a in settings.INSTALLED_APPS if a.startswith('h1ds_')]
    

class H1DSTitleNode(template.Node):
    def render(self, context):
        try:
            return settings.H1DS_TITLE
        except:
            return ""

def do_h1ds_title(parser, token):
    """Returns the value of H1DS_TITLE in settings.py"""
    return H1DSTitleNode()

class H1DSHeaderNode(template.Node):
    def render(self, context):
        subtitle_string_list = []
        for app in h1ds_installed_apps:
            if app != 'h1ds_core':
                app_module =  __import__(app, globals(), locals(), [])
                app_doc_name = app_module.MODULE_DOC_NAME
                homepage_url_name = app.replace('_', '-')+'-homepage'
                homepage_url = reverse(homepage_url_name)
                subtitle_string_list.append('<a href="%s">%s</a>' %(homepage_url, app_doc_name))
        if hasattr(settings, 'H1DS_EXTRA_SUBLINKS'):
            subtitle_string_list.extend(['<a href="%s">%s</a>' %(i[1], i[0]) for i in settings.H1DS_EXTRA_SUBLINKS])
        subtitle_strings = " &middot; ".join(subtitle_string_list)
        if hasattr(settings, 'H1DS_TITLE'):
            title = settings.H1DS_TITLE
        else:
            title = "H1 Data Server"            
        return_string = '<div id="title"><h1><a href="/">%s</a></h1>' %(title)
        return_string += '<div id="subtitle">'+subtitle_strings+'</div></div>'
        return return_string

def do_h1ds_header(parser, token):
    """This populates the H1DS header, providing links to H1DS modules."""
    return H1DSHeaderNode()

class H1DSFooterNode(template.Node):
    def render(self, context):
        app_strings = []
        for app in h1ds_installed_apps:
            try:
                app_module =  __import__('.'.join([app, 'version']), globals(), locals(), [])
                app_urls = app_module.version.get_module_urls()
                app_strings.append('<a href="%s"><strong>%s</strong></a> %s (<a href="%s">[bug/feature request]</a>)' %(app_urls[0], app, app_module.version.get_version(), app_urls[1]))
            except:
                app_strings.append("<strong>%s</strong>" %app)
        return '<p>%s</p>' %" &middot; ".join(app_strings)

def do_h1ds_footer(parser, token):
    """This populates the H1DS footer, showing registered H1DS modules with version numbers."""
    return H1DSFooterNode()

register.tag('h1ds_title', do_h1ds_title)
register.tag('h1ds_header', do_h1ds_header)
register.tag('h1ds_footer', do_h1ds_footer)
do_h1ds_title.is_safe = True
do_h1ds_header.is_safe = True
do_h1ds_footer.is_safe = True

