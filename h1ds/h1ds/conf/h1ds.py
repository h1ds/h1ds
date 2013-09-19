# -*- coding: iso-8859-1 -*-
"""
    MoinMoin - modern theme
    
    Modified by Dave Pretty for PRL

    @copyright: 2003-2005 Nir Soffer, Thomas Waldmann
    @license: GNU GPL, see COPYING for details.
"""

def login_logout(d):
    
    if d["user_name"] == "":
        content =  u'<a href="/openid/login/">log in</a>'
    else:
        content =  u'%(username)s // <a href="/user/settings/%(username)s">settings</a> // <a href="/logout/">logout</a>' %{'username':d["user_name"]}
    return u'<div id="loginlinks">' + content + "</div>"
        

from MoinMoin.theme import ThemeBase
from MoinMoin import wikiutil
from MoinMoin.Page import Page
from h1ds.templatetags import h1ds_headfoot
from django.conf import settings as django_settings

class Theme(ThemeBase):

    name = "h1ds"


    def html_head(self, d):
        extra_line = u'<script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>'
        return ThemeBase.html_head(self, d) + '\n' + extra_line

    def header(self, d, **kw):
        """ Assemble wiki header

        @param d: parameter dictionary
        @rtype: unicode
        @return: page header html
        """
        h1ds_header = h1ds_headfoot.H1DSHeaderNode()
        context = ""
        h1ds_header_string = unicode(h1ds_header.render(context))

        
        html = [
            # Pre header custom html
            self.emit_custom_html(self.cfg.page_header1),

            u'<div id="container">',
            # Header
            u'<header class="clearfix">',
            u'<div class="fixed-centre">',
            login_logout(d),
            self.searchform(d),
            h1ds_header_string,
            u'</div>',
            u'</header>',
            u'<div class="wikibar">',
            u'<div class="fixed-centre clearfix">',
            self.editbar(d),
            u'</div>',
            u'</div>',
            u'<div class="messagebar">',
            u'<div class="fixed-centre clearfix">',
            self.msg(d),
            u'</div>',
            u'</div>',

            # Post header custom html (not recommended)
            self.emit_custom_html(self.cfg.page_header2),
            u'<div id="main" role="main" class="clearfix fixed-centre">',

            # Start of page
            self.startPage(),
        ]
        return u'\n'.join(html)

    def editorheader(self, d, **kw):
        return self.header(d, **kw)

    def _old_editorheader(self, d, **kw):
        """ Assemble wiki header for editor

        @param d: parameter dictionary
        @rtype: unicode
        @return: page header html
        """
        html = [
            # Pre header custom html
            self.emit_custom_html(self.cfg.page_header1),

            # Header
            u'<div id="header">',
            self.title(d),
            self.msg(d),
            u'</div>',

            # Post header custom html (not recommended)
            self.emit_custom_html(self.cfg.page_header2),

            # Start of page
            self.startPage(),
        ]
        return u'\n'.join(html)

    def h1ds_footer(self, d, **keywords):
        h1ds_footer = h1ds_headfoot.H1DSFooterNode()
        context = ""
        return unicode(h1ds_footer.render(context))

    def google_tracker(self, d, **keywords):
        tracker = h1ds_headfoot.H1DSGoogleTrackerNode()
        context = ""
        return unicode(tracker.render(context))
    
    def footer(self, d, **keywords):
        """ Assemble wiki footer

        @param d: parameter dictionary
        @keyword ...:...
        @rtype: unicode
        @return: page footer html
        """
        page = d['page']
        html = [
            u'</div>', #closes #id main
            # End of page
            self.pageinfo(page),
            self.endPage(),

            # Pre footer custom html (not recommended!)
            self.emit_custom_html(self.cfg.page_footer1),

            # Footer
            u'<div class="wikibar">',
            u'<div class="fixed-centre clearfix">',
            self.editbar(d),
            u'</div>',
            u'</div>',
            u'<footer>',
            u'<div class="fixed-centre clearfix">',
            #self.credits(d),
            #self.showversion(d, **keywords),
            u'<div id="h1dsfooter">',
            self.h1ds_footer(d, **keywords),
            u'</div>',
            u'</div>', # close fixed-centre, clearfix
            u'</footer>',
            u'</div>', # close id="container"
            u'<script src="//ajax.googleapis.com/ajax/libs/jquery/1.6.2/jquery.min.js"></script>',
            u"<script>window.jQuery || document.write('<script src="+u'"%sjs/libs/jquery-1.6.2.min.js"' %(django_settings.STATIC_URL) + u"><\/script>')</script>",
            u'<script defer src="%sjs/plugins.js"></script>' %(django_settings.STATIC_URL),
            u'<script defer src="%sjs/script.js"></script>' %(django_settings.STATIC_URL),
            u'<script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>',
            self.guiEditorScript(d),
            self.google_tracker(d, **keywords),
            u'<!--[if lt IE 7 ]>',
            u'<script src="//ajax.googleapis.com/ajax/libs/chrome-frame/1.0.3/CFInstall.min.js"></script>',
            u"<script>window.attachEvent('onload',function(){CFInstall.check({mode:'overlay'})})</script>",
            u'<![endif]-->',


            # Post footer custom html
            self.emit_custom_html(self.cfg.page_footer2),
            ]
        return u'\n'.join(html)


    def send_title(self, text, **keywords):
        """
        Output the page header (and title).

        @param text: the title text
        @keyword page: the page instance that called us - using this is more efficient than using pagename..
        @keyword pagename: 'PageName'
        @keyword print_mode: 1 (or 0)
        @keyword editor_mode: 1 (or 0)
        @keyword media: css media type, defaults to 'screen'
        @keyword allow_doubleclick: 1 (or 0)
        @keyword html_head: additional <head> code
        @keyword body_attr: additional <body> attributes
        @keyword body_onload: additional "onload" JavaScript code
        """
        request = self.request
        _ = request.getText
        rev = request.rev

        if keywords.has_key('page'):
            page = keywords['page']
            pagename = page.page_name
        else:
            pagename = keywords.get('pagename', '')
            page = Page(request, pagename)
        if keywords.get('msg', ''):
            raise DeprecationWarning("Using send_page(msg=) is deprecated! Use theme.add_msg() instead!")
        scriptname = request.script_root

        # get name of system pages
        page_front_page = wikiutil.getFrontPage(request).page_name
        page_help_contents = wikiutil.getLocalizedPage(request, 'HelpContents').page_name
        page_title_index = wikiutil.getLocalizedPage(request, 'TitleIndex').page_name
        page_site_navigation = wikiutil.getLocalizedPage(request, 'SiteNavigation').page_name
        page_word_index = wikiutil.getLocalizedPage(request, 'WordIndex').page_name
        page_help_formatting = wikiutil.getLocalizedPage(request, 'HelpOnFormatting').page_name
        page_find_page = wikiutil.getLocalizedPage(request, 'FindPage').page_name
        home_page = wikiutil.getInterwikiHomePage(request) # sorry theme API change!!! Either None or tuple (wikiname,pagename) now.
        page_parent_page = getattr(page.getParentPage(), 'page_name', None)

        # Prepare the HTML <head> element
        user_head = [request.cfg.html_head]

        # include charset information - needed for moin_dump or any other case
        # when reading the html without a web server
        user_head.append('''<meta http-equiv="Content-Type" content="%s;charset=%s">\n''' % (page.output_mimetype, page.output_charset))

        meta_keywords = request.getPragma('keywords')
        meta_desc = request.getPragma('description')
        if meta_keywords:
            user_head.append('<meta name="keywords" content="%s">\n' % wikiutil.escape(meta_keywords, 1))
        if meta_desc:
            user_head.append('<meta name="description" content="%s">\n' % wikiutil.escape(meta_desc, 1))

        # search engine precautions / optimization:
        # if it is an action or edit/search, send query headers (noindex,nofollow):
        if request.query_string:
            user_head.append(request.cfg.html_head_queries)
        elif request.method == 'POST':
            user_head.append(request.cfg.html_head_posts)
        # we don't want to have BadContent stuff indexed:
        elif pagename in ['BadContent', 'LocalBadContent', ]:
            user_head.append(request.cfg.html_head_posts)
        # if it is a special page, index it and follow the links - we do it
        # for the original, English pages as well as for (the possibly
        # modified) frontpage:
        elif pagename in [page_front_page, request.cfg.page_front_page,
                          page_title_index, 'TitleIndex',
                          page_find_page, 'FindPage',
                          page_site_navigation, 'SiteNavigation',
                          'RecentChanges', ]:
            user_head.append(request.cfg.html_head_index)
        # if it is a normal page, index it, but do not follow the links, because
        # there are a lot of illegal links (like actions) or duplicates:
        else:
            user_head.append(request.cfg.html_head_normal)

        if 'pi_refresh' in keywords and keywords['pi_refresh']:
            user_head.append('<meta http-equiv="refresh" content="%d;URL=%s">' % keywords['pi_refresh'])

        # output buffering increases latency but increases throughput as well
        output = []
        # later: <html xmlns=\"http://www.w3.org/1999/xhtml\">
        output.append("""\
<!doctype html>
<!--[if lt IE 7]> <html class="no-js ie6 oldie" lang="en"> <![endif]-->
<!--[if IE 7]>    <html class="no-js ie7 oldie" lang="en"> <![endif]-->
<!--[if IE 8]>    <html class="no-js ie8 oldie" lang="en"> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js" lang="en"> <!--<![endif]-->
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
  <title>%(title)s</title>
  <meta name="description" content="">
  <meta name="author" content="">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <link rel="stylesheet" href="%(static_url)scss/style.css">
  <script src="%(static_url)sjs/libs/moin.common.js"></script>
<script type="text/javascript">
<!--
var search_hint = "Search";
//-->
</script>
  <script src="%(static_url)sjs/libs/modernizr-2.0.6.min.js"></script>
""" %{'title':text, 'static_url':django_settings.STATIC_URL})

        # Links
        output.append('<link rel="Start" href="%s">\n' % request.href(page_front_page))
        if pagename:
            output.append('<link rel="Alternate" title="%s" href="%s">\n' % (
                    _('Wiki Markup'), request.href(pagename, action='raw')))
            output.append('<link rel="Alternate" media="print" title="%s" href="%s">\n' % (
                    _('Print View'), request.href(pagename, action='print')))

            # !!! currently disabled due to Mozilla link prefetching, see
            # http://www.mozilla.org/projects/netlib/Link_Prefetching_FAQ.html
            #~ all_pages = request.getPageList()
            #~ if all_pages:
            #~     try:
            #~         pos = all_pages.index(pagename)
            #~     except ValueError:
            #~         # this shopuld never happend in theory, but let's be sure
            #~         pass
            #~     else:
            #~         request.write('<link rel="First" href="%s/%s">\n' % (request.script_root, quoteWikinameURL(all_pages[0]))
            #~         if pos > 0:
            #~             request.write('<link rel="Previous" href="%s/%s">\n' % (request.script_root, quoteWikinameURL(all_pages[pos-1])))
            #~         if pos+1 < len(all_pages):
            #~             request.write('<link rel="Next" href="%s/%s">\n' % (request.script_root, quoteWikinameURL(all_pages[pos+1])))
            #~         request.write('<link rel="Last" href="%s/%s">\n' % (request.script_root, quoteWikinameURL(all_pages[-1])))

            if page_parent_page:
                output.append('<link rel="Up" href="%s">\n' % request.href(page_parent_page))

        # write buffer because we call AttachFile
        request.write(''.join(output))
        output = []

        # XXX maybe this should be removed completely. moin emits all attachments as <link rel="Appendix" ...>
        # and it is at least questionable if this fits into the original intent of rel="Appendix".
        if pagename and request.user.may.read(pagename):
            from MoinMoin.action import AttachFile
            AttachFile.send_link_rel(request, pagename)

        output.extend([
            '<link rel="Search" href="%s">\n' % request.href(page_find_page),
            '<link rel="Index" href="%s">\n' % request.href(page_title_index),
            '<link rel="Glossary" href="%s">\n' % request.href(page_word_index),
            '<link rel="Help" href="%s">\n' % request.href(page_help_formatting),
                      ])

        output.append("</head>\n")
        request.write(''.join(output))
        output = []

        # start the <body>
        bodyattr = []
        if keywords.has_key('body_attr'):
            bodyattr.append(' ')
            bodyattr.append(keywords['body_attr'])

        # Add doubleclick edit action
        if (pagename and keywords.get('allow_doubleclick', 0) and
            not keywords.get('print_mode', 0) and
            request.user.edit_on_doubleclick):
            if request.user.may.write(pagename): # separating this gains speed
                url = page.url(request, {'action': 'edit'})
                bodyattr.append(''' ondblclick="location.href='%s'" ''' % wikiutil.escape(url, True))

        # Set body to the user interface language and direction
        bodyattr.append(' %s' % self.ui_lang_attr())

        body_onload = keywords.get('body_onload', '')
        if body_onload:
            bodyattr.append(''' onload="%s"''' % body_onload)
        output.append('\n<body%s>\n' % ''.join(bodyattr))

        # Output -----------------------------------------------------------

        # If in print mode, start page div and emit the title
        if keywords.get('print_mode', 0):
            d = {
                'title_text': text,
                'page': page,
                'page_name': pagename or '',
                'rev': rev,
            }
            request.themedict = d
            output.append(self.startPage())
            output.append(self.interwiki(d))
            output.append(self.title(d))

        # In standard mode, emit theme.header
        else:
            exists = pagename and page.exists(includeDeleted=True)
            # prepare dict for theme code:
            d = {
                'theme': self.name,
                'script_name': scriptname,
                'title_text': text,
                'logo_string': request.cfg.logo_string,
                'site_name': request.cfg.sitename,
                'page': page,
                'rev': rev,
                'pagesize': pagename and page.size() or 0,
                # exists checked to avoid creation of empty edit-log for non-existing pages
                'last_edit_info': exists and page.lastEditInfo() or '',
                'page_name': pagename or '',
                'page_find_page': page_find_page,
                'page_front_page': page_front_page,
                'home_page': home_page,
                'page_help_contents': page_help_contents,
                'page_help_formatting': page_help_formatting,
                'page_parent_page': page_parent_page,
                'page_title_index': page_title_index,
                'page_word_index': page_word_index,
                'user_name': request.user.name,
                'user_valid': request.user.valid,
                'msg': self._status,
                'trail': keywords.get('trail', None),
                # Discontinued keys, keep for a while for 3rd party theme developers
                'titlesearch': 'use self.searchform(d)',
                'textsearch': 'use self.searchform(d)',
                'navibar': ['use self.navibar(d)'],
                'available_actions': ['use self.request.availableActions(page)'],
            }

            # add quoted versions of pagenames
            newdict = {}
            for key in d:
                if key.startswith('page_'):
                    if not d[key] is None:
                        newdict['q_'+key] = wikiutil.quoteWikinameURL(d[key])
                    else:
                        newdict['q_'+key] = None
            d.update(newdict)
            request.themedict = d

            # now call the theming code to do the rendering
            if keywords.get('editor_mode', 0):
                output.append(self.editorheader(d))
            else:
                output.append(self.header(d))

        # emit it
        request.write(''.join(output))
        output = []
        self._send_title_called = True


def execute(request):
    """
    Generate and return a theme object

    @param request: the request object
    @rtype: MoinTheme
    @return: Theme object
    """
    return Theme(request)

