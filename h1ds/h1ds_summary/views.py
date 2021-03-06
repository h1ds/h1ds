from urlparse import urlparse, urlunparse
import itertools
from django.contrib import messages
from django.core.cache import cache
from django.core.urlresolvers import resolve, reverse
from django.http import QueryDict, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.generic import View, FormView
from django.core.exceptions import MultipleObjectsReturned, PermissionDenied

from celery import group

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from h1ds.views import JSONNumpyRenderer
from rest_framework.renderers import YAMLRenderer
from rest_framework.renderers import XMLRenderer
from rest_framework import serializers

from h1ds.views import DeviceListView
from h1ds.models import Device, Shot
from h1ds_summary.db import SummaryTable
from h1ds_summary.forms import SummaryAttributeForm, ControlPanelForm, RawSqlForm
from h1ds_summary.models import SummaryAttribute
from h1ds_summary.parsers import get_attribute_variants
from h1ds_summary.tasks import insert_or_update_single_table_attribute, update_from_shot_slug
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404


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
        device = Device.objects.get(slug=kwargs['device'])
        #latest_shot = get_latest_shot_from_summary_table(device)
        table = SummaryTable(device)
        latest_shot = table.get_latest_shot()
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


# TODO: bring this back to life
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
        device = Device.objects.get(slug=kwargs['device'])
        table = SummaryTable(device)
        if 'shot' in request.POST:
            shot_instance = Shot(number=int(request.POST.get("shot")), device=device)
            table.update_shot(shot_instance)
        elif 'attribute' in request.POST:
            attribute = request.POST.get("attribute")
            table.update_attribute(attribute)
        return HttpResponseRedirect(return_path)


class AddSummaryAttribiteView(View):
    # Take a HTTP post with  a filled SummaryAttributeForm, and create a
    # SummaryAttribute instance.
    # TODO: provide forms with return url, especially when

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        device = Device.objects.get(slug=kwargs['device'])
        summary_attribute_form = SummaryAttributeForm(request.POST)
        if summary_attribute_form.is_valid():
            summary_attribute = summary_attribute_form.save(commit=False)
            summary_attribute.device = device
            summary_attribute.save()
            return_url = request.POST.get('return_url', reverse("h1ds-summary-homepage"))
            return HttpResponseRedirect(return_url)
        else:
            return render_to_response('h1ds_summary/form.html',
                                      {'form': summary_attribute_form,
                                       'device': device,
                                       'submit_url': reverse('add-summary-attribute', args=args, kwargs=kwargs)},
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

    shot_str = kwargs["shot"]
    device = Device.objects.get(slug=kwargs['device'])

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
    # json_data = json.loads(url_response.content)

    # Now we generalise the URL  for any shot, replacing the shot number
    # with __shot__
    general_url = attr_url_json.replace(shot_str, "__shot__")

    # Create a SummaryAttributeForm with URL and data type entries pre-filled
    summary_attribute_form = SummaryAttributeForm(initial={'source': general_url})

    # If the request is from AJAX, return form in JSON format
    # TODO: provide ajax / sidebar attribute adding.
    # if request.is_ajax():

    # Otherwise, forward user to form entry page
    return render_to_response('h1ds_summary/form.html',
                              {'form': summary_attribute_form,
                               'device': device,
                               'submit_url': reverse('add-summary-attribute', kwargs={'device': device.slug})},
                              context_instance=RequestContext(request))


def go_to_source(request, device, slug, shot):
    """Go to the H1DS web interface corresponding to the summary data."""

    attr = SummaryAttribute.objects.get(slug__iexact=slug, device__slug=device)
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


##########################################################
## New Django REST Framework based views
##########################################################


class RawSQLView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONNumpyRenderer, YAMLRenderer, XMLRenderer,)

    # to protect against SQL injection attacks, only allow users with permissions to do raw SQL queries.
    @method_decorator(permission_required('h1ds_summary.raw_sql_query_summaryattribute'))
    def dispatch(self, *args, **kwargs):
        return super(RawSQLView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect("/")

    def post(self, request, *args, **kwargs):
        form = RawSqlForm(request.POST)
        if form.is_valid():
            device = Device.objects.get(slug=form.cleaned_data['device'])
            table = SummaryTable(device)
            select_list = [i.strip() for i in form.cleaned_data['select'].split(',')]
            if not 'shot' in select_list:
                select_list.insert(0, 'shot')
            results = table.do_query(select=select_list, where=form.cleaned_data['where'])
            # TODO: non html
            return Response({'data': results,
                             'device': device,
                             'inactive_attributes': [],
                             'active_attributes': [],
                             'sql_form': form},
                            template_name='h1ds_summary/summary_table.html')
        else:  # invalid form
            # TODO: proper handling here
            return HttpResponseRedirect("/")


class SimpleSerializer(serializers.Serializer):
    def to_native(self, obj):
        return obj


class SummaryView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONNumpyRenderer, YAMLRenderer, XMLRenderer,)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        device_instance = get_object_or_404(Device, slug=kwargs['device'])
        if not device_instance.user_is_allowed(request.user):
            raise PermissionDenied
        return super(SummaryView, self).dispatch(request, *args, **kwargs)

    def get_attribute_links(self, request, *args, **kwargs):
        """Get links and info about attributes which can be added or removed from the current table.

        Returns:
            showable_attributes, hideable_attributes - both are lists of dicts

        Both showable_attributes and hideableattributes have the format [attr_a, attr_b, ...], where attr_x is
        {slug:, url:, name:, description:}

        """
        # TODO: remove duplication here, we already have grabbed the device in self.get()
        device = Device.objects.get(slug=kwargs.get("device"))
        table = SummaryTable(device)
        all_attrs = table.get_attributes_from_table(filter_initial_attributes=True)
        shot_str = kwargs.get("shot_str", DEFAULT_SHOT_REGEX)
        attr_str = kwargs.get("attr_str", DEFAULT_ATTR_STR)
        filter_str = kwargs.get("filter_str", DEFAULT_FILTER)
        attr_variants = get_attribute_variants(device=device, all_attrs=all_attrs, attr_str=attr_str)

        showable_attribute = []
        hideable_attributes = []

        for attr in attr_variants:
            attr_instance = SummaryAttribute.objects.get(device=device, slug=attr['slug'])
            if filter_str:
                attr_url = reverse('sdfsummary', kwargs={'device': device.slug, 'shot_str': shot_str,
                                                         'attr_str': attr['attr_str'],
                                                         'filter_str': filter_str})
            else:
                attr_url = reverse('sdsummary', kwargs={'device': device.slug, 'shot_str': shot_str, 'attr_str': attr['attr_str']})

            attr_dict = {'slug': attr['slug'], 'url': attr_url,
                         'name': attr_instance.name, 'description': attr_instance.description}
            if attr['is_active']:
                hideable_attributes.append(attr_dict)
            else:
                showable_attribute.append(attr_dict)

        return showable_attribute, hideable_attributes

    def get(self, request, *args, **kwargs):

        device_slug = kwargs.get("device")

        shot_str = kwargs.get("shot_str", DEFAULT_SHOT_REGEX)
        attr_str = kwargs.get("attr_str", DEFAULT_ATTR_STR)
        filter_str = kwargs.get("filter_str", DEFAULT_FILTER)

        device = Device.objects.get(slug=device_slug)
        table = SummaryTable(device)

        results = table.do_query_from_path_components(shot_str, attr_str, filter_str)
        # TODO: HTML version w/ templates...

        if request.accepted_renderer.format == 'html':
            if not results:
                return Response(template_name='h1ds_summary/no_data.html')

            inactive_attributes, active_attributes = self.get_attribute_links(request, *args, **kwargs)
            sql_form = RawSqlForm(initial={'device': device.slug})
            return Response({'data': results,
                             'device': device,
                             'inactive_attributes': inactive_attributes,
                             'active_attributes': active_attributes,
                             'sql_form': sql_form},
                            template_name='h1ds_summary/summary_table.html')

        serializer = SimpleSerializer(results)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        device_slug = kwargs.get("device")
        shot_str = kwargs.get("shot_str", DEFAULT_SHOT_REGEX)
        update_from_shot_slug(device_slug, shot_str)
        # TODO: sensible user feedback
        return HttpResponseRedirect("/")


class SummaryDeviceListView(DeviceListView):
    def get_template_names(self):
        return ("h1ds_summary/device_list.html", )

    def get(self, request, *args, **kwargs):
        # If there is only one device, then show the device detail view rather than list devices.
        try:
            return redirect('h1ds-summary-device-homepage', device=self.get_queryset().get().slug)
        except (Device.DoesNotExist, MultipleObjectsReturned):
            # TODO: we should treat Device.DoesNotExist separately with a message to create a device.
            return self.list(request, *args, **kwargs)


def get_shot_for_device(device):
    def get_shot(number):
        try:
            return Shot.objects.get(number=number, device=device)
        except Shot.DoesNotExist:
            return None
    return get_shot


## Non-API view (currenly html-only control panel) - TODO: allow contorl via api
class ControlPanelView(FormView):
    template_name = 'h1ds_summary/control_panel.html'
    form_class = ControlPanelForm

    def get_initial(self):
        return {'device': self.kwargs['device']}

    @method_decorator(permission_required('h1ds_summary.raw_sql_query_summaryattribute'))
    def dispatch(self, *args, **kwargs):
        return super(ControlPanelView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        device = Device.objects.get(slug=self.kwargs['device'])
        cleaned_data = form.get_cleaned_data_for_device(device)

        shots_with_timestamps = ((s.number, s.timestamp) for s in map(get_shot_for_device(device), cleaned_data['shots']) if s is not None)

        # TODO: doing every (shot, attr) as separate commit - v. v. poor performace. fix this soon.
        shot_attr_pairs = itertools.product(shots_with_timestamps, cleaned_data['attributes'])
        g = group(insert_or_update_single_table_attribute.s(device.slug, x[0][0], x[0][1], x[1]) for x in shot_attr_pairs)
        g.apply_async()
        # TODO: sensible user feedback
        return HttpResponseRedirect("/")



