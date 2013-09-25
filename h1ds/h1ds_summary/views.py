import json
import datetime
from urlparse import urlparse, urlunparse

from django import forms
from django.contrib import messages
from django.core.cache import cache
from django.core.urlresolvers import resolve, reverse
from django.db import connection
from django.db.models import Max
from django.http import QueryDict, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.utils import simplejson
from django.views.decorators.cache import never_cache
from django.views.generic import View
from django.utils.importlib import import_module
from django.conf import settings

#from h1ds.base import get_latest_shot_function
from h1ds.models import Node

from h1ds_summary import SUMMARY_TABLE_NAME
from h1ds_summary.forms import SummaryAttributeForm
from h1ds_summary.models import SummaryAttribute
from h1ds_summary.utils import parse_shot_str, parse_attr_str, parse_filter_str, get_latest_shot_from_summary_table
from h1ds_summary.tasks import populate_summary_table_task, populate_attribute_task


DEFAULT_SHOT_REGEX = "last30"
DEFAULT_ATTR_STR = "default"
DEFAULT_FILTER = None


def get_format(request, default='html'):
    """get format URI query key.

    Fall back to 'view' for backwards compatability.

    """
    format_ = request.GET.get('format', None)
    if not format_:
        format_ = request.GET.get('view', default)
    return format_


class NoAttributeException(Exception):
    pass


class NoShotException(Exception):
    pass


class AJAXLatestSummaryShotView(View):
    """Return latest shot."""

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        latest_shot = get_latest_shot_from_summary_table()
        return HttpResponse('{"latest_shot":"%s"}' % latest_shot, 'application/javascript')


class AJAXLastUpdateTimeView(View):
    """Return value of timestamp cache which is updated whenever summarydb is updated"""

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        last_update = cache.get('last_summarydb_update')
        if last_update:
            return HttpResponse('{"last_update":"%s"}' % str(last_update.isoformat()), 'application/javascript')
        else:
            # last_summarydb_update not in cache...
            return HttpResponse('{"last_update":"null"}', 'application/javascript')


class SummaryMixin(object):
    def get_attr_slugs(self, request, *args, **kwargs):
        attr_str = kwargs.get("attr_str", DEFAULT_ATTR_STR)
        return parse_attr_str(attr_str)


    def get_summary_data(self, request, *args, **kwargs):
        shot_str = kwargs.get("shot_str", DEFAULT_SHOT_REGEX)
        attr_str = kwargs.get("attr_str", DEFAULT_ATTR_STR)
        filter_str = kwargs.get("filter_str", DEFAULT_FILTER)
        table = kwargs.get("table", SUMMARY_TABLE_NAME)

        # If there are no summary attributes, then tell the user
        if SummaryAttribute.objects.count() == 0:
            raise NoAttributeException
            #return self.no_attribute_response(request)

        attribute_slugs = self.get_attr_slugs(request, *args, **kwargs)

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
                # TODO: might work for html only - either pass get query(to get format value - html, json etc) or use per-format method
                return HttpResponseRedirect(reverse('sdfsummary',
                                                    kwargs={'shot_str': shot_str, 'attr_str': new_attr_str,
                                                            'filter_str': filter_str}))
            else:
                # TODO: might work for html only - either pass get query(to get format value - html, json etc) or use per-format method
                return HttpResponseRedirect(
                    reverse('sdsummary', kwargs={'shot_str': shot_str, 'attr_str': new_attr_str}))

        select_list = ['shot']
        select_list.extend(attribute_slugs)
        select_str = ','.join(select_list)

        shot_where = parse_shot_str(shot_str)
        if shot_where == None:
            #return self.no_shot_response(request)
            raise NoShotException

        if filter_str == None:
            where = shot_where
        else:
            filter_where = parse_filter_str(filter_str)
            where = ' AND '.join([shot_where, filter_where])

        cursor = connection.cursor()
        cursor.execute(
            "SELECT %(select)s FROM %(table)s WHERE %(where)s ORDER BY -shot" % {'table': table, 'select': select_str,
                                                                                 'where': where})
        data = cursor.fetchall()

        # Format data as specified in SummaryAttribute
        # TODO: should make this optional

        # Make a dict of format strings for summary attributes so we don't
        # have to look them up inside the loop.
        format_strings = {}
        for att in SummaryAttribute.objects.all():
            format_strings[att.slug] = att.format_string

        new_data = []
        data_headers = select_str.split(',')
        for d in data:
            new_row = []
            for j_i, j in enumerate(d):
                fstr = format_strings.get(data_headers[j_i], None)
                try:
                    val = fstr % j
                except TypeError:
                    val = j
                new_row.append(val)
            new_data.append(new_row)

        return (new_data, select_str, table, where)


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')

        return json.JSONEncoder.default(self, obj)


class JSONSummaryResponseMixin(SummaryMixin):
    http_method_names = ['get']

    def no_attribute_response(self, request):
        return HttpResponse(json.dumps({'error': 'Summary database has no attributes..'}, cls=MyEncoder),
                            mimetype='application/json')

    def get(self, request, *args, **kwargs):
        data, select_str, table, where = self.get_summary_data(request, *args, **kwargs)

        annotated_data = [{'d': i, 'shot': i[0]} for i in data][::-1]

        d = {
            'timestamp': str(datetime.datetime.now().isoformat()),
            'attributes': select_str.split(','),
            'data': annotated_data,
        }
        return HttpResponse(json.dumps(d, cls=MyEncoder), mimetype='application/json')


class HTMLSummaryResponseMixin(SummaryMixin):
    http_method_names = ['get']

    def no_attribute_response(self, request):
        return render_to_response('h1ds_summary/no_attributes.html', {},
                                  context_instance=RequestContext(request))

    def no_shot_response(self, request):
        return render_to_response('h1ds_summary/no_shots.html', {},
                                  context_instance=RequestContext(request))

    def get(self, request, *args, **kwargs):
        shot_str = kwargs.get("shot_str", DEFAULT_SHOT_REGEX)

        q = self.get_summary_data(request, *args, **kwargs)

        # TODO need to fix get_summary_data so it doesn't return REsponse object...
        summary_data = self.get_summary_data(request, *args, **kwargs)

        try:
            (data, select_str, table, where) = summary_data
        except ValueError:
            # TODO: fix this hack!
            return summary_data

        attribute_slugs = self.get_attr_slugs(request, *args, **kwargs)
        excluded_attribute_slugs = SummaryAttribute.objects.exclude(slug__in=attribute_slugs).values_list('slug',
                                                                                                          flat=True)


        # This seems a bit messy, but  it's not clear to me how to refer
        # to a summary data value's  attribute slug name from within the
        # template, so let's attach it here...

        new_data = []
        data_headers = select_str.split(',')
        for d in data:
            new_row = [(j, data_headers[j_i]) for j_i, j in enumerate(d)]
            new_data.append(new_row)

        # should we poll server for shot updates?
        poll_server = 'last' in shot_str

        return render_to_response('h1ds_summary/summary_table.html',
                                  {'data': new_data, 'data_headers': data_headers,
                                   # TODO: use an API provided by h1ds to get latest shot...
                                   'latest_shot': 0, #get_latest_shot(),
                                   'included_attrs': attribute_slugs,
                                   'poll_server': poll_server,
                                   'excluded_attrs': excluded_attribute_slugs},
                                  context_instance=RequestContext(request))


class MultiSummaryResponseMixin(JSONSummaryResponseMixin, HTMLSummaryResponseMixin):
    """Dispatch to requested representation."""

    representations = {
        "html": HTMLSummaryResponseMixin,
        "json": JSONSummaryResponseMixin,
    }

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method for requested representation;
        # if a method doesn't exist, defer to the error handler.
        # Also defer to the error handler if the request method isn't on the approved list.

        # TODO: for now, we only support GET and POST, as we are using the query string to
        # determing which representation should be used, and the querydict is only available
        # for GET and POST. Need to bone up on whether query strings even make sense on other
        # HTTP verbs. Probably, we should use HTTP headers to figure out which content type should be
        # returned - also, we might be able to support both URI and header based content type selection.
        # http://stackoverflow.com/questions/381568/rest-content-type-should-it-be-based-on-extension-or-accept-header
        # http://www.xml.com/pub/a/2004/08/11/rest.html

        if request.method == 'GET':
            requested_representation = get_format(request).lower()
        elif request.method == 'POST':
            requested_representation = get_format(request)
        else:
            # until we figure out how to determine appropriate content type
            return self.http_method_not_allowed(request, *args, **kwargs)

        if not requested_representation in self.representations:
            # TODO: should handle this and let user know? rather than ignore?
            requested_representation = 'html'

        rep_class = self.representations[requested_representation]

        if request.method.lower() in rep_class.http_method_names:
            handler = getattr(rep_class, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        self.request = request
        self.args = args
        self.kwargs = kwargs
        try:
            return handler(self, request, *args, **kwargs)
        except NoAttributeException:
            return rep_class.no_attribute_response(self, request)
        except NoShotException:
            return rep_class.no_shot_response(self, request)


class SummaryView(MultiSummaryResponseMixin, View):
    pass


class RecomputeSummaryView(View):
    """Recompute requested subset of summary database.

    Require a HTTP POST with two key-value pairs: 'return_path and either 'shot' or 'attribute'.
       return_path - URL to be redirected to after we submit the processing task to the job queue.
       shot - a single shot number, for which all attributes are recomputed.
       attribute - name (slug) of an attribute to be recomputed for all shots.

    If both shot and attribute are provided, the shot number will be processed and the attribute ignored.
    """

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        return_path = request.POST.get("return_path")
        if request.POST.has_key("shot"):
            shot = [int(request.POST.get("shot")), ]
            populate_summary_table_task.delay(shot)
        elif request.POST.has_key("attribute"):
            attribute = request.POST.get("attribute")
            populate_attribute_task.delay(attribute)
        return HttpResponseRedirect(return_path)


class AddSummaryAttribiteView(View):
    # Take a HTTP post with  a filled SummaryAttributeForm, and create a
    # SummaryAttribute instance.
    # TODO: provide forms with return url, especially when

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        summary_attribute_form = SummaryAttributeForm(request.POST)
        if summary_attribute_form.is_valid():
            summary_attribute_form.save()
            return_url = request.POST.get('return_url', reverse("h1ds-summary-homepage"))
            return HttpResponseRedirect(return_url)
        else:
            return render_to_response('h1ds_summary/form.html',
                                      {'form': summary_attribute_form,
                                       'submit_url': reverse('add-summary-attribute')},
                                      context_instance=RequestContext(request))


def get_summary_attribute_form_from_url(request):
    """Take a H1DS web URL and return a SummaryAttributeForm.

    The request should contain a 'url' POST query with a URL pointing to
    a data node (can include  filters).  The URL must point to a
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

    # Now we can update the URL query string to enforce the JSON format.
    parsed_url_list[4] = '&'.join([parsed_url[4], 'format=json'])

    # And here is our original URL with format=json query added
    attr_url_json = urlunparse(parsed_url_list)

    # Get the django view function corresponding to the URL path
    view, args, kwargs = resolve(parsed_url_list[2])

    node_ancestry = kwargs['nodepath'].split("/")
    node = Node.datatree.get_node_from_ancestry(node_ancestry)

    #url_processor = URLProcessor(url=kwargs['url'])
    # Create a  new query  dict from the  queries in the  requested URL,
    # i.e. data filters, etc...
    new_query = QueryDict(parsed_url_list[4]).copy()

    # Insert our new query dict into the request sent to this view...
    request.GET = new_query

    # use HTTP GET, not POST
    request.method = "GET"
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
    general_url = attr_url_json.replace(str(node.shot.number), "__shot__")

    # Create a SummaryAttributeForm with URL and data type entries pre-filled
    summary_attribute_form = SummaryAttributeForm(initial={'source': general_url})

    # If the request is from AJAX, return form in JSON format
    # TODO: provide ajax / sidebar attribute adding.
    # if request.is_ajax():

    # Otherwise, forward user to form entry page
    return render_to_response('h1ds_summary/form.html',
                              {'form': summary_attribute_form, 'submit_url': reverse('add-summary-attribute')},
                              context_instance=RequestContext(request))


def go_to_source(request, slug, shot):
    """Go to the H1DS web interface corresponding to the summary data."""

    attr = SummaryAttribute.objects.get(slug__iexact=slug)
    if attr.source.startswith('http://'):
        source_url = attr.source.replace('__shot__', str(shot))

        # add format=html HTML query

        parsed_url_list = [i for i in urlparse(source_url)]

        parsed_url_list[4] = '&'.join([parsed_url_list[4], 'format=html'])

        source_html_url = urlunparse(parsed_url_list)
    else:
        # TODO: don't annoy user with this - remove link on attributes which don't come from h1ds interface.
        messages.info(request, "Cannot get link to H1DS, this attribute is not generated by filters")
        source_html_url = request.META.get('HTTP_REFERER', '/')
    return HttpResponseRedirect(source_html_url)


class RawSqlForm(forms.Form):
    select = forms.CharField(widget=forms.Textarea)
    where = forms.CharField(widget=forms.Textarea)


def raw_sql(request, tablename=SUMMARY_TABLE_NAME):
    """Provide a form for users to request a raw SQL query and display the results.

    """
    # to protect against SQL injection attacks, only allow users with permissions to do raw SQL queries.
    if not request.user.has_perm('h1ds_summary.raw_sql_query_summaryattribute'):
        return HttpResponseRedirect("/")

    if request.method == 'POST':
        form = RawSqlForm(request.POST)
        if form.is_valid():
            cursor = connection.cursor()
            select_list = [i.strip() for i in form.cleaned_data['select'].split(',')]
            if select_list[0] != 'shot':
                _select_list = ['shot']
                _select_list.extend(select_list)
                select_list = _select_list
            cursor.execute(
                "SELECT %s FROM %s WHERE %s" % (','.join(select_list), tablename, form.cleaned_data['where']))
            data = cursor.fetchall()

            new_data = []
            data_headers = select_list
            for d in data:
                new_row = []
                for j_i, j in enumerate(d):
                    new_row.append((j, data_headers[j_i]))
                new_data.append(new_row)

            return render_to_response('h1ds_summary/summary_table.html',
                                      {'data': new_data, 'data_headers': data_headers, 'select': ','.join(select_list),
                                       'where': form.cleaned_data['where']},
                                      context_instance=RequestContext(request))

    if request.method == 'GET':
        return HttpResponseRedirect("/")
