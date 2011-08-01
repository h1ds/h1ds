# -*- coding: iso-8859-1 -*-
"""
    MoinMoin - modern theme
    
    Modified by Dave Pretty for PRL

    @copyright: 2003-2005 Nir Soffer, Thomas Waldmann
    @license: GNU GPL, see COPYING for details.
"""

def login_logout(d):
    if d["user_name"] == "":
        return u'<p><a href="/openid/login/">Log in</a></p>'
    else:
        return u'<p>%(username)s // <a href="/user/settings/%(username)s">settings</a> // <a href="/logout/">logout</a></p>' %{'username':d["user_name"]}

        

from MoinMoin.theme import ThemeBase
from h1ds_core.templatetags import h1ds_headfoot


class Theme(ThemeBase):

    name = "h1ds"

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

            # Header
            u'<div id="header">',
            #self.logo(),
            #self.username(d),
            login_logout(d),
            #u'<div id="locationline">',
            self.searchform(d),
            #self.interwiki(d),
            #self.title(d),
            #u'</div>',
            h1ds_header_string,
            #self.trail(d),
            #self.navibar(d),
            #u'<hr id="pageline">',
            #u'<div id="pageline"><hr style="display:none;"></div>',
            u'</div>',
            u'<div id="wikibar">',
            self.msg(d),
            self.editbar(d),
            u'</div>',

            # Post header custom html (not recommended)
            self.emit_custom_html(self.cfg.page_header2),

            # Start of page
            self.startPage(),
        ]
        return u'\n'.join(html)

    def editorheader(self, d, **kw):
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
    
    def footer(self, d, **keywords):
        """ Assemble wiki footer

        @param d: parameter dictionary
        @keyword ...:...
        @rtype: unicode
        @return: page footer html
        """
        page = d['page']
        html = [
            # End of page
            self.pageinfo(page),
            self.endPage(),

            # Pre footer custom html (not recommended!)
            self.emit_custom_html(self.cfg.page_footer1),

            # Footer
            u'<div id="footer">',
            self.editbar(d),
            #self.credits(d),
            #self.showversion(d, **keywords),
            u'<div id="h1dsfooter">',
            self.h1ds_footer(d, **keywords),
            u'</div>',
            u'</div>',

            # Post footer custom html
            self.emit_custom_html(self.cfg.page_footer2),
            ]
        return u'\n'.join(html)


def execute(request):
    """
    Generate and return a theme object

    @param request: the request object
    @rtype: MoinTheme
    @return: Theme object
    """
    return Theme(request)

