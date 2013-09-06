from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

register = template.Library()

h1ds_installed_apps = []
for app in settings.INSTALLED_APPS:
    if app.startswith('h1ds_'):
        h1ds_installed_apps.append(app)

h1ds_ignore = ['h1ds_core']

google_track_script = ("<script type=\"text/javascript\">var _gaq = _gaq || "
                       "[];_gaq.push(['_setAccount', 'GOOGLE_TRACKING_ID']);"
                       "_gaq.push(['_trackPageview']);(function() {var ga = "
                       "document.createElement('script'); ga.type = "
                       "'text/javascript'; ga.async = true;ga.src = "
                       "('https:' == document.location.protocol ? 'https://ssl'"
                       " : 'http://www') + '.google-analytics.com/ga.js';var s "
                       "= document.getElementsByTagName('script')[0]; "
                       "s.parentNode.insertBefore(ga, s);})();</script>")


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
        subtitle_string_list = ['<a href="/data">Data</a>']
        for app in h1ds_installed_apps:
            if app not in h1ds_ignore:
                app_module =  __import__(app, globals(), locals(), [])
                app_doc_name = app_module.MODULE_DOC_NAME
                homepage_url_name = app.replace('_', '-')+'-homepage'
                homepage_url = reverse(homepage_url_name)
                html_str = '<a href="%s">%s</a>' % (homepage_url, app_doc_name)
                subtitle_string_list.append(html_str)
        if hasattr(settings, 'H1DS_EXTRA_SUBLINKS'):
            sublinks = []
            for name, url, doc in settings.H1DS_EXTRA_SUBLINKS:
                sublinks.append('<a href="%s">%s</a>' %(url, name))
            subtitle_string_list.extend(sublinks)
        subtitle_strings = " &middot; ".join(subtitle_string_list)
        if hasattr(settings, 'H1DS_TITLE'):
            title = settings.H1DS_TITLE
        else:
            title = "H1 Data Server"            
        return_string = '<div id="title"><h1><a href="/">%s</a></h1>' % (title)
        return_string += '<div id="subtitle">'+subtitle_strings+'</div></div>'
        return return_string

def do_h1ds_header(parser, token):
    """This populates the H1DS header, providing links to H1DS modules."""
    return H1DSHeaderNode()

class H1DSFooterNode(template.Node):
    def render(self, context):
        app_string = ('<a href="%s"><strong>%s</strong></a> %s '
                      '[<a href="%s">bug/feature request</a>]')
        app_strings = []
        for app in h1ds_installed_apps:
            try:
                version_mod = '.'.join([app, 'version'])
                app_module =  __import__(version_mod, globals(), locals(), [])
                app_urls = app_module.version.get_module_urls()
                app_version = app_module.version.get_version()
                app_strings.append(app_string %(app_urls[0], app,
                                                app_version, app_urls[1]))
            except:
                app_strings.append("<strong>%s</strong>" %app)
        return '<p>%s</p>' %" &middot; ".join(app_strings)

def do_h1ds_footer(parser, token):
    """Populate the H1DS footer.

    Show registered H1DS modules with version numbers.

    """
    return H1DSFooterNode()

class H1DSGoogleTrackerNode(template.Node):
    def render(self, context):
        if hasattr(settings, 'GOOGLE_TRACKING_ID'):
            tracking_string = google_track_script.replace(
                "GOOGLE_TRACKING_ID", settings.GOOGLE_TRACKING_ID)
        else:
            tracking_string = ""
        return tracking_string

def do_google_tracker(parser, token):
    """If settings contain GOOGLE_TRACKER_ID, then add tracking script."""
    return(H1DSGoogleTrackerNode())



register.tag('h1ds_title', do_h1ds_title)
register.tag('h1ds_header', do_h1ds_header)
register.tag('h1ds_footer', do_h1ds_footer)
register.tag('google_tracker', do_google_tracker)

do_h1ds_title.is_safe = True
do_h1ds_header.is_safe = True
do_h1ds_footer.is_safe = True
do_google_tracker.is_safe = True
