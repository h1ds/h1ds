"""
Note, don't confuse  H1DS Data nodes with Django template  nodes. Try to
make each type obvious by their name.
"""
import inspect
from django import template
from django.core.urlresolvers import reverse
from django.utils.html import escape

register = template.Library()

class H1DSDataTemplateNode(template.Node):
    def __init__(self, node_name):
        self.node_var = template.Variable(node_name)
    def render(self, context):
        try:
            node = self.node_var.resolve(context)
            return ('<div class="centrecontent">'
                    '<div class="data">%s</div>'
                    '</div>' %(node.get_format('html')))
        except template.VariableDoesNotExist:
            return ''

def display_data(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, data_name = token.split_contents()
    except ValueError:
        msg = "%r tag requires a single argument" % token.contents.split()[0]
        raise template.TemplateSyntaxError, msg
    return H1DSDataTemplateNode(data_name)


register.tag('display_data', display_data)

filter_html = """\
<div class="sidebarcontent">
 <form action="%(submit_url)s">
  <span class="left" title="%(text)s">%(clsname)s</span>
  <span class="right">%(input_str)s<input type="submit" title="add" value="+"/></span>
  <input type="hidden" name="filter" value="%(clsname)s">
  <input type="hidden" name="path" value="%(path)s">%(input_query)s
 </form>
</div>"""


active_filter_html = """\
<div class="sidebarcontent">
 <form action="%(update_url)s">
  <span class="left" title="%(text)s">%(clsname)s</span>
  <span class="right">%(input_str)s
   <input type="hidden" name="fid" value="%(fid)s">
   <input title="update" type="submit" value="u"/>
  </span>
  <input type="hidden" name="filter" value="%(clsname)s">
  <input type="hidden" name="path" value="%(path)s">%(input_query)s
 </form>
 <span class="right">
  <form action="%(remove_url)s">
   <input type="hidden" name="path" value="%(path)s">
   <input type="hidden" name="fid" value="%(fid)s">
   <input title="remove" type="submit" value="-"/>%(existing_query)s
  </form>
 </span>
</div>
"""

def get_filter(context, f_class, is_active=False, f_id=None, f_data=None):
    try:
        request = context['request']
        hidden_input = '<input type="hidden" name="{}" value="{}" />'
        existing_query_string = ""
        for k, v in request.GET.items():
            existing_query_string += hidden_input.format(k, v)
        arg_list = f_class.kwarg_names
        docstring = inspect.getdoc(f_class)
        if is_active:
            arg_input = ('<input title="%(name)s" type="text" '
                         'size=5 name="%(name)s" value="%(value)s">')
            if f_data == None:
                f_data = []
            update_url = reverse("update-filter")
            remove_url = reverse("remove-filter")
            input_str = ''
            for i, j in enumerate(arg_list):
                input_str += arg_input % {'name': j, 'value': f_data[j]}

            return_string = active_filter_html % {
                'update_url': update_url,
                'text': docstring,
                'input_str': input_str,
                'clsname': f_class.slug,
                'path': request.path,
                'input_query': existing_query_string,
                'fid': f_id,
                'remove_url': remove_url,
                'existing_query': existing_query_string,
                }
            return return_string

        else:
            submit_url = reverse("apply-filter")
            arg_input = ('<input title="%(name)s" type="text" size=5 '
                         'name="%(name)s" placeholder="%(name)s">')
            input_str = ""
            for j in arg_list:
                input_str += arg_input % {'name': j}
            return_string =  filter_html % {'text': docstring,
                                           'input_str': input_str,
                                           'clsname': f_class.slug,
                                           'submit_url': submit_url,
                                           'path': request.path,
                                           'input_query': existing_query_string}
            return return_string
    except template.VariableDoesNotExist:
        #return ''
        raise

@register.simple_tag(takes_context=True)
def show_filters(context, data_node):
    # TODO: HACK
    filters = ""
    for n, f in data_node.get_available_filters().iteritems():
        filters += get_filter(context, f)
    return filters

@register.simple_tag(takes_context=True)
def show_active_filters(context, data_node):
    active_filters = ""
    for fid, f, fdata in data_node.filter_history:
        active_filters += get_filter(context, f, is_active=True,
                                     f_id=fid, f_data=fdata)
    
    return active_filters

@register.simple_tag(takes_context=True)
def show_info(context, data_node):
    # TODO
    return ""#"TODO... dtype: %s" % escape(str(type(data_node.data.data)))

@register.simple_tag(takes_context=True)
def get_url_for_shot(context, url, new_shot):
    #input_shot = shot_regex.findall(url)[0]
    print "temp hack - not working"
    return url#url.replace(str(input_shot), str(new_shot))

class GetAbsoluteUriNode(template.Node):
    def __init__(self):
        pass

    def render(self, context):
        try:
            request = context['request']
            return request.build_absolute_uri()

        except template.VariableDoesNotExist:
            return ''

def get_absolute_uri(parser, token):
    return GetAbsoluteUriNode()

register.tag('get_absolute_uri', get_absolute_uri)

class GetTreeURLNode(template.Node):
    def __init__(self, url_processor, tree):
        self.url_processor = template.Variable(url_processor)
        self.tree = template.Variable(tree)

    def render(self, context):
        try:
            url_p = self.url_processor.resolve(context)
            t = self.tree.resolve(context)
            return url_p.get_url_for_tree(t)

        except template.VariableDoesNotExist:
            return ''

def get_tree_url(parser, token):
    try:
        tag_name, url_processor, tree = token.split_contents()
    except ValueError:
        msg = "%r tag requires three arguments" % token.contents.split()[0]
        raise template.TemplateSyntaxError, msg
    return GetTreeURLNode(url_processor, tree)

register.tag('get_tree_url', get_tree_url)


