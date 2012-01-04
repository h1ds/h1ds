
from django.shortcuts import render_to_response
from django.core.cache import cache
from django.db.models import Max
from django.views.decorators.cache import never_cache
from django.utils import simplejson
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django import forms
from django.db import connection
from django.core.urlresolvers import reverse
from django.contrib import messages

from h1ds_summary.models import SummaryAttribute

DEFAULT_SHOT_REGEX = "last10"

def do_html_data(data, attr_list):
    output_data = []
    for row in data:
        row_data = [row[0]]
        for attr_i,attr_data in enumerate(row[1:]):
            attr_value = attr_data
            if attr_list[attr_i].display_format:
                try:
                    attr_value = attr_list[attr_i].display_format %(attr_data)
                except:
                    pass
            row_data.append({'val':attr_value, 'norm':int(100.0*attr_list[attr_i].normalise(attr_data)), 'col':attr_list[attr_i].colourise(attr_data), 'show_barplot':attr_list[attr_i].show_barplot()})
        output_data.append(row_data)
    return output_data


def get_vis_attr_data(path, attr_list):
    if len(attr_list) == 1:
        return [{'att':attr_list[0], 'newpath':None}]
    output = []
    spl_path = path.split("/")
    if len(spl_path) == 3: # path=/summary/ -> add default shots and another trailing /
        spl_path[2] = DEFAULT_SHOT_REGEX
        spl_path.append("")
    if len(spl_path) == 4:
        spl_path[3] = 'all'
        spl_path.append("")
    for att in attr_list:
        newpath = '+'.join([i.slug for i in attr_list if not i==att])
        spl_path[3] = newpath
        output.append({'att':att, 'newpath':'/'.join(spl_path)})
    return output


def get_hidden_attr_data(path, attr_list, n_cols=2):
    all_attrs = SummaryAttribute.objects.all()
    output = []
    spl_path=path.split('/')
    if len(spl_path) == 3: # path=/summary/ -> add default shots and another trailing /
        spl_path[2] = DEFAULT_SHOT_REGEX
        spl_path.append("")
    tmp_path = '+'.join([i.slug for i in attr_list])
    for a in all_attrs:
        if not a in attr_list:
            spl_path[3] = "+".join([tmp_path, a.slug])
            output.append({'att':a, 'newpath':'/'.join(spl_path)})
    sorted_list = sorted(output, key=lambda k: k['att'].slug.lower())
    sorted_output = []
    n_rows = float(len(sorted_list))/n_cols
    n_delta =int( n_rows)
    if n_rows%1 != 0:
        n_rows +=1
    n_rows = int(n_rows)
    for j in range(n_rows):
        sorted_output.extend(sorted_list[j::n_rows])
    return sorted_output

@never_cache
def latest_shot(request, format="html"):
    latest_shot = cache.get("latest_summary_shot", 0)
    view = request.GET.get('view', 'html')
    if not latest_shot > 0:
        latest_shot = Shot.objects.aggregate(Max('shot'))['shot__max']
        #cache.set("latest_summary_shot", latest_shot, 60*60*6)
        cache.set("latest_summary_shot", latest_shot, 3)
    if view == 'xml':
        xmlstr = """<?xml version="1.0" encoding="UTF-8" ?>
        <shot>
        <number>%d</number>
        <comment>Latest shot in summary database</comment>
        </shot>""" %latest_shot
        return HttpResponse(xmlstr, mimetype='text/xml; charset=utf-8')
    else:
        return render_to_response('summary/latest_shot.html', {'shot':latest_shot}, context_instance=RequestContext(request))


@never_cache
def ajax_latest_shot(request):
    latest_shot = cache.get("latest_summary_shot", 0)
    if not latest_shot > 0:
        latest_shot = Shot.objects.aggregate(Max('shot'))['shot__max']
        #cache.set("latest_summary_shot", latest_shot, 60*60*6)
        cache.set("latest_summary_shot", latest_shot, 3)

    d = {'shot':latest_shot}
    return HttpResponse(simplejson.dumps(d))


########################################################################
### NEW CODE                                                         ###
########################################################################

import json
from urlparse import urlparse, urlunparse

from django.core.urlresolvers import resolve
from django.http import QueryDict
from django.shortcuts import redirect
from h1ds_summary import SUMMARY_TABLE_NAME
from h1ds_summary.forms import SummaryAttributeForm
from h1ds_summary.utils import parse_shot_str, parse_attr_str, parse_filter_str
from django.views.generic import View

class SummaryView(View):
    
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        shot_str=kwargs.get("shot_str", "last10")
        attr_str=kwargs.get("attr_str", "default")
        filter_str=kwargs.get("filter_str", None)
        table=kwargs.get("table", SUMMARY_TABLE_NAME)
        

        # If there are no summary attributes, then tell the user
        if SummaryAttribute.objects.count() == 0:
            return render_to_response('h1ds_summary/no_attributes.html', {}, 
                                      context_instance=RequestContext(request))
        
        attribute_slugs = parse_attr_str(attr_str)
                                         
        show_attrs = request.GET.get('show_attr', None)
        hide_attrs = request.GET.get('hide_attr', None)

        if show_attrs or hide_attrs:
            if show_attrs:
                new_attrs = show_attrs.split('+')
                attribute_slugs.extend(new_attrs)
            if hide_attrs:
                for a in hide_attrs.split('+'):
                    try:
                        attribute_slugs.remove(a)
                    except ValueError:
                        pass
            if len(attribute_slugs) == 0:
                new_attr_str = "default"
            else:
                new_attr_str = '+'.join(attribute_slugs)
            if filter_str:
                return redirect(summary, shot_str=shot_str, attr_str=new_attr_str, filter_str = filter_str)
            else:
                return redirect(summary, shot_str=shot_str, attr_str=new_attr_str)

        select_list = ['shot']
        select_list.extend(attribute_slugs)
        select_str = ','.join(select_list)

        excluded_attribute_slugs = SummaryAttribute.objects.exclude(slug__in=attribute_slugs).values_list('slug', flat=True)

        shot_where = parse_shot_str(shot_str)
        if shot_where == None:
            return render_to_response('h1ds_summary/no_shots.html', {}, context_instance=RequestContext(request))

        if filter_str == None:
            where = shot_where
        else:
            filter_where = parse_filter_str(filter_str)
            where = ' AND '.join([shot_where, filter_where])

        cursor = connection.cursor()
        cursor.execute("SELECT %(select)s FROM %(table)s WHERE %(where)s ORDER BY -shot" %{'table':table, 'select':select_str, 'where':where})
        data = cursor.fetchall()

        # This seems a bit messy, but  it's not clear to me how to refer
        # to a summary data value's  attribute slug name from within the
        # template, so let's attach it here...

        new_data = []
        data_headers = select_str.split(',')
        for d in data:
            new_row = []
            for j_i, j in enumerate(d):
                new_row.append((j, data_headers[j_i]))
            new_data.append(new_row)

        return render_to_response('h1ds_summary/summary_table.html',
                                  {'data':new_data, 'data_headers':data_headers,
                                   'included_attrs':attribute_slugs,
                                   'excluded_attrs':excluded_attribute_slugs},
                                  context_instance=RequestContext(request))



def add_summary_attribute(request):
    # Take a HTTP post with  a filled SummaryAttributeForm, and create a
    # SummaryAttribute instance.
    # TODO: provide forms with return url, especially when 
    if request.method == 'POST':
        summary_attribute_form = SummaryAttributeForm(request.POST)
        if summary_attribute_form.is_valid():
            summary_attribute_form.save()
            return_url = request.POST.get('return_url', reverse("h1ds-summary-homepage"))
            return HttpResponseRedirect(return_url)            
        else:
            return render_to_response('h1ds_summary/form.html',
                                      {'form': summary_attribute_form,
                                       'submit_url':reverse('add-summary-attribute')},
                                      context_instance=RequestContext(request))
            
    else:
        return HttpResponseRedirect(reverse("h1ds-summary-homepage"))
    

def get_summary_attribute_form_from_url(request):
    """Take a H1DS mdsplus web URL and return a SummaryAttributeForm.

    The request should contain a 'url' POST query with a URL pointing to
    a mdsplus data node (can include  filters).  The URL must point to a
    path in the same django instance.

    We first call the URL and check what datatype is returned so we know
    which SQL datatype to use, then we pre-fill a form to be complete by
    the user.
    """
    # Get the requested URL from the POST data
    attr_url = request.POST['url']

    # Split URL into [scheme, netloc, path, params, query, fragments]
    parsed_url = urlparse(attr_url)

    # parsed_url is an immutable ParseResult instance, copy it to a (mutable) list
    parsed_url_list = [i for i in parsed_url]

    # Now we can update the URL query string to enforce the JSON view.
    parsed_url_list[4] = '&'.join([parsed_url[4], 'view=json'])

    # And here is our original URL with view=json query added
    attr_url_json = urlunparse(parsed_url_list)

    # Get the django view function corresponding to the URL path
    view, args, kwargs = resolve(parsed_url_list[2])

    # Create a  new query  dict from the  queries in the  requested URL,
    # i.e. data filters, etc...
    new_query = QueryDict(parsed_url_list[4]).copy()

    # Insert our new query dict into the request sent to this view...
    request.GET = new_query    

    # use HTTP GET, not POST
    request.method="GET"
    request.POST = None
    
    # ...and use this request to call the view function and get the data
    # for the requested URL.
    kwargs['request'] = request
    url_response = view(*args, **kwargs)

    # url_response content is a string, let's convert it to a dictionary
    # using the json parser.
    json_data = json.loads(url_response.content)    

    # Now we generalise the URL  for any shot, replacing the shot number
    # with __shot__
    general_url = attr_url_json.replace(kwargs['shot'], "__shot__")

    # Create a SummaryAttributeForm with URL and data type entries pre-filled
    summary_attribute_form = SummaryAttributeForm(initial={'source':general_url})

    # If the request is from AJAX, return form in JSON format
    # TODO: provide ajax / sidebar attribute adding.
    # if request.is_ajax():

    # Otherwise, forward user to form entry page
    return render_to_response('h1ds_summary/form.html',
                              {'form': summary_attribute_form, 'submit_url':reverse('add-summary-attribute')},
                              context_instance=RequestContext(request))
    
def go_to_source(request, slug, shot):
    """Go to the MDSplus web interface corresponding to the summary data."""

    
    attr = SummaryAttribute.objects.get(slug__iexact=slug)
    if attr.source.startswith('http://'):
        source_url = attr.source.replace('__shot__', str(shot))
    
        # add view=html HTML query
    
        parsed_url_list = [i for i in urlparse(source_url)]
        
        parsed_url_list[4] = '&'.join([parsed_url_list[4], 'view=html'])
        
        source_html_url = urlunparse(parsed_url_list)
    else:
        # TODO: don't annoy user with this - remove link on attributes which don't come from MDS interface.
        messages.info(request, "Cannot get link to MDSplus, this attribute is not generated by filters")
        source_html_url = request.META.get('HTTP_REFERER', '/')
    return HttpResponseRedirect(source_html_url)


class RawSqlForm(forms.Form):
    select = forms.CharField(widget=forms.Textarea)
    where = forms.CharField(widget=forms.Textarea)


def raw_sql(request, tablename=SUMMARY_TABLE_NAME):
    """Provide a form for users to request a raw SQL query and display the results.
    
    """
    # to protect against SQL injection attacks, only allow users with permissions to do raw SQL queries.
    # TODO: separate permission for raw sql? add summaryattribute should catch all users in editor group...
    if not request.user.has_perm('h1ds_summary.add_summaryattribute'):
        return HttpResponseRedirect("/")
    
    if request.method == 'POST':
        form = RawSqlForm(request.POST)
        if form.is_valid():
            cursor=connection.cursor()
            select_list = form.cleaned_data['select'].split(',')
            if select_list[0] != 'shot':
                _select_list = ['shot']
                _select_list.extend(select_list)
                select_list = _select_list
            cursor.execute("SELECT %s FROM %s WHERE %s" %(','.join(select_list), tablename, form.cleaned_data['where']))
            data = cursor.fetchall()

            new_data = []
            data_headers = select_list
            for d in data:
                new_row = []
                for j_i, j in enumerate(d):
                    new_row.append((j, data_headers[j_i]))
                new_data.append(new_row)

            return render_to_response('h1ds_summary/summary_table.html',
                                      {'data':new_data, 'data_headers':data_headers, 'select':','.join(select_list), 'where':form.cleaned_data['where']},
                                       context_instance=RequestContext(request))

    if request.method == 'GET':
        return HttpResponseRedirect("/")

