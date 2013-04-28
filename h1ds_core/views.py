import csv
import inspect
import re
import xml.etree.ElementTree as etree
import json
import time
import StringIO
import numpy as np

import pylab

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.core import serializers
from django.http import HttpResponse, StreamingHttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django import forms
from django.views.generic import View, ListView, DetailView, RedirectView
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.conf import settings
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured

from h1ds_core.models import H1DSSignalInstance, Worksheet
from h1ds_core.models import UserSignal, UserSignalForm
from h1ds_core.base import get_filter_list, get_latest_shot_function

data_module = import_module(settings.H1DS_DATA_MODULE)
URLProcessor = getattr(data_module, 'URLProcessor')
Node = getattr(data_module, 'Node')
get_trees = getattr(data_module, 'get_trees')


get_latest_shot = get_latest_shot_function()

def get_shot_stream_generator():
    def new_shot_generator():
        latest_shot = get_latest_shot()
        while True:
            time.sleep(1)
            tmp = get_latest_shot()
            if tmp != latest_shot:
                latest_shot = tmp
                yield "{}\n".format(latest_shot)
    return new_shot_generator
    
new_shot_generator = get_shot_stream_generator()

### TEMP ###
#import h1ds_core.filters
from h1ds_core.base import get_all_filters
############
all_filters = get_all_filters()

def get_format(request, default='html'):
    """get format URI query key.

    Fall back to 'view' for backwards compatability.

    """
    format_ =  request.GET.get('format', None)
    if not format_:
        format_ = request.GET.get('view', default)
    return format_

    
def homepage(request):
    """Return the H1DS homepage."""
    return render_to_response('h1ds_core/homepage.html', 
                              context_instance=RequestContext(request))

def logout_view(request):
    """Log the user out of H1DS."""
    logout(request)
    return redirect('/')
            

class ChangeProfileForm(forms.Form):
    username = forms.CharField(max_length=30, help_text="Please use CamelCase, with each word capitalised. For example: MarkOliphant or LymanSpitzer")
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()


class UserMainView(ListView):

    def get_queryset(self):
        return Worksheet.objects.filter(user=self.request.user)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserMainView, self).dispatch(*args, **kwargs)

class WorksheetView(DetailView):

    def get_object(self):
        w = get_object_or_404(Worksheet, user__username=self.kwargs['username'], slug=self.kwargs['worksheet'])
        if w.is_public or w.user == self.request.user:
            return w
        else:
            raise PermissionDenied


@login_required
def edit_profile(request, username=''):
    if request.user.username == username:
        if request.method == 'POST':
            form = ChangeProfileForm(request.POST)
            if form.is_valid():
                u = User.objects.get(username=username)
                u.username = form.cleaned_data['username']
                u.first_name = form.cleaned_data['first_name']
                u.last_name = form.cleaned_data['last_name']
                u.email = form.cleaned_data['email']
                u.save()
                return redirect('/')
                
            else:
                data = {'username':username, 
                        'first_name':request.user.first_name,
                        'last_name':request.user.last_name,
                        'email':request.user.email}
                user_form = ChangeProfileForm(data)
                return render_to_response('h1ds_core/userprofile.html', 
                                          {'form':user_form, 'return_url':'/user/profile/%s/' %username},
                                          context_instance=RequestContext(request))
        else:
            data = {'username':username, 
                    'first_name':request.user.first_name,
                    'last_name':request.user.last_name,
                    'email':request.user.email}
            user_form = ChangeProfileForm(data)
            return render_to_response('h1ds_core/userprofile.html', 
                                      {'form':user_form},
                                      context_instance=RequestContext(request))
    else:
        return redirect('/')


def get_max_fid(request):
    # get maximum filter number
    filter_list = get_filter_list(request)
    if len(filter_list) == 0:
        max_filter_num = 0
    else:
        max_filter_num = max([i[0] for i in filter_list])
    return max_filter_num

class FilterBaseView(RedirectView):
    """Read in filter info from HTTP query and apply H1DS filter syntax.

    The request GET query must contain  a field named 'filter' which has
    the filter function  name as its value. Separate fields  for each of
    the filter arguments  are also required, where the  argument name is
    as it appears in the filter function code.

    If  overwrite_fid is  False,  the new  filter will  have  an FID  +1
    greater than the highest existing  filter. If overwrite_fid is True,
    we expect a query field with an fid to overwrite.
    
    TODO: Do  we really  need path  to be passed  explicitly as  a query
    field? or can we  use session info? - largest FID  is taken from the
    request, but we return url from path... can't be good.
    TODO: kwargs are not yet supported for filter functions.
    """
    
    http_method_name = ['get']

    def get_filter_url(self, overwrite_fid=False):
        # Get name of filter function
        qdict = self.request.GET.copy()
        filter_name = qdict.pop('filter')[-1]

        # Get the actual filter function
        #filter_function = getattr(df, filter_name)
        filter_class = all_filters[filter_name]
        
        # We'll append the filter to this path and redirect there.
        return_path = qdict.pop('path')[-1]

        if overwrite_fid:
            fid = int(qdict.pop('fid')[-1])
            for k,v in qdict.items():
                if k.startswith('f%d' %fid):
                    qdict.pop(k)
        else:
            # Find the maximum fid in the existing query and +1
            fid = get_max_fid(self.request)+1

        # We expect the filter arguments to be passed as key&value in the HTTP query.
        #filter_arg_names = inspect.getargspec(filter_function).args[1:]
        #filter_arg_values = [qdict.pop(a)[-1] for a in filter_arg_names]
        filter_arg_values = [qdict.pop(a)[-1] for a in filter_class.kwarg_names]

        # add new filter to query dict
        qdict.update({'f%d' %(fid):filter_name})
        #for argn, arg_val in enumerate(filter_arg_values):
        #    qdict.update({'f%d_arg%d' %(fid,argn):arg_val})
        for name, val in zip(filter_class.kwarg_names, filter_arg_values):
            qdict.update({'f%d_%s' %(fid,name):val})

        return '?'.join([return_path, qdict.urlencode()])

class ApplyFilterView(FilterBaseView):
    def get_redirect_url(self, **kwargs):
        return self.get_filter_url()

class UpdateFilterView(FilterBaseView):
    def get_redirect_url(self, **kwargs):
        return self.get_filter_url(overwrite_fid=True)

class RemoveFilterView(RedirectView):

    http_method_names = ['get']

    def get_redirect_url(self, **kwargs):
        qdict = self.request.GET.copy()
        filter_id = int(qdict.pop('fid')[-1])
        return_path = qdict.pop('path')[-1]
        new_filter_values = []
        for k,v in qdict.items():
            if k.startswith('f%d' %filter_id):
                qdict.pop(k)
        return '?'.join([return_path, qdict.urlencode()])




class UserSignalCreateView(CreateView):

    form_class = UserSignalForm

    def get_success_url(self):
        return self.request.POST.get('url', "/")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.ordering = 1 # TODO
        self.object.url = self.request.POST.get('url', "/")
        self.object.save()
        return super(UserSignalCreateView, self).form_valid(form)


class UserSignalUpdateView(UpdateView):
    model = UserSignal

    def get_success_url(self):
        return self.request.POST.get('redirect_url', "/")

    def get_context_data(self, **kwargs):
        context = super(UserSignalUpdateView, self).get_context_data(**kwargs)
        context['redirect_url'] = self.request.GET.get('redirect_url', "/")
        return context

class UserSignalDeleteView(DeleteView):
    model = UserSignal

    def get_success_url(self):
        return self.request.POST.get('url', "/")


        
class ShotStreamView(View):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        return StreamingHttpResponse(new_shot_generator())


class RequestShotView(RedirectView):
    """Redirect to shot, as requested by HTTP post."""

    http_method_names = ['post']

    def get_redirect_url(self, **kwargs):
        shot = self.request.POST['go_to_shot']
        input_path = self.request.POST['reqpath']
        url = URLProcessor(url=input_path)
        url.shot = int(shot)
        return url.get_url()

class AJAXShotRequestURL(View):
    """Return URL modified for requested shot"""

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        input_path = request.GET.get('input_path')
        shot = int(request.GET.get('shot'))
        url_processor = URLProcessor(url=input_path)
        #input_shot = shot_regex.findall(input_path)[0]
        url_processor.shot = shot
        #new_url = input_path.replace("/"+str(input_shot)+"/", "/"+str(shot)+"/")
        new_url = url_processor.get_url()
        output_json = '{"new_url":"%s"}' %new_url
        return HttpResponse(output_json, 'application/javascript')

def xml_latest_shot(request):
    """Hack to get IDL client working again - this should be merged with other latest shot view"""
    
    shot = str(get_latest_shot())
    # TODO - get URI from settings, don't hardwire h1svr
    response_xml = etree.Element('{http://h1svr.anu.edu.au/data}dataurlmap',
                             attrib={'{http://www.w3.org/XML/1998/namespace}lang': 'en'})
    
    shot_number = etree.SubElement(response_xml, 'shot_number', attrib={})
    shot_number.text = shot
    return HttpResponse(etree.tostring(response_xml), mimetype='text/xml; charset=utf-8')

class AJAXLatestShotView(View):
    """Return latest shot."""
    
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        format_ = get_format(request, default='json')
        if format_.lower() == 'xml':
            return xml_latest_shot(request)
        latest_shot = get_latest_shot()
        return HttpResponse('{"latest_shot":"%s"}' %latest_shot, 'application/javascript')

def request_url(request):
    """Return the URL for the requested parameters."""
    
    shot = request.GET['shot']
    path = request.GET['path']
    tree = request.GET['tree']

    
    url_xml = etree.Element('{http://h1svr.anu.edu.au/}dataurlmap',
                             attrib={'{http://www.w3.org/XML/1998/namespace}lang': 'en'})
    
    shot_number = etree.SubElement(url_xml, 'shot_number', attrib={})
    shot_number.text = shot
    data_path = etree.SubElement(url_xml, 'path', attrib={})
    data_path.text = path
    data_tree = etree.SubElement(url_xml, 'tree', attrib={})
    data_tree.text = tree

    url_processor = URLProcessor(shot=int(shot), tree=tree, path=path)
    url = url_processor.get_url()
    url_el = etree.SubElement(url_xml, 'url', attrib={})
    url_el.text = url

    return HttpResponse(etree.tostring(url_xml), mimetype='text/xml; charset=utf-8')


####

class JSONNodeResponseMixin(object):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        
        response_data = {'labels':self.node.label}
        if self.node.get_data() == None:
            response_data['data'] = None
            response_data['dim'] = None
        elif np.isscalar(self.node.get_data()):
            response_data['data'] = np.asscalar(self.node.get_data())
            response_data['dim'] = None
        elif len(self.node.get_data().shape) == 1:
            response_data['data'] = self.node.get_data().tolist()
            response_data['dim'] = self.node.get_dim().tolist()
        elif 1 < len(self.node.get_data().shape) <= 3:
            data, dim = [],[]
            for i in self.node.get_data():
                if hasattr(i, "tolist"):
                    data.append(i.tolist())
                else:
                    data.append(i)
            for i in self.node.get_dim():
                if hasattr(i, "tolist"):
                    dim.append(i.tolist())
                else:
                    dim.append(i)
            response_data['data'] =  data
            response_data['dim'] = dim
        else:
            response_data['data'] = "unknown data"
            response_data['dim'] = None
        metadata = {
            'path':unicode(self.node.url_processor.path),
            'tree':self.node.url_processor.tree,
            'shot':self.node.url_processor.shot,
            'summary_dtype':self.node.get_summary_dtype(),
            }
        # add metadata...
        response_data.update({'meta':metadata})
        return HttpResponse(json.dumps(response_data), mimetype='application/json')

class CSVNodeResponseMixin(object):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        data = self.node.get_format('csv')
        
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=data.csv'

        writer = csv.writer(response)
        for i in data:
            writer.writerow(map(str, i))
        return response


class XMLNodeResponseMixin(object):
    """TODO: Generalise this for all datatypes"""

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        # TODO (depecated - much code change): this should be handled by wrappers
        # however, at present self.node.get_view
        # calls get_view on the data object which
        # doesn't ?? know about shot info, etc
        # the proper fix might be to have wrappers
        # take as args wrappers rather than data objects?
        
        data_xml = etree.Element('{http://h1svr.anu.edu.au/data}data',
                                 attrib={'{http://www.w3.org/XML/1998/namespace}lang': 'en'})

        # add shot info
        shot_number = etree.SubElement(data_xml, 'shot_number', attrib={})
        shot_number.text = str(self.node.url_processor.shot)
        ## TODO: add metadata (for mds, shot time can go into metadata)
        #shot_time = etree.SubElement(data_xml, 'shot_time', attrib={})
        #shot_time.text = str(self.node.get_data_time())
        

        # add data info
        tree = etree.SubElement(data_xml, 'tree', attrib={})
        tree.text = self.node.url_processor.tree
        path = etree.SubElement(data_xml, 'path', attrib={})
        path.text = self.node.url_processor.path

        signal = etree.SubElement(data_xml, 'data', attrib={'type':'signal'})

        ## make xlink ? to signal binary 
        ## for now, just text link
        #### should use proper url joining rather than string hacking...
        signal.text = request.build_absolute_uri()
        if '?' in signal.text:
            # it doesn't matter if we have multiple 'format' get queries - only the last one is used
            signal.text += '&format=bin' 
        else:
            signal.text += '?format=bin'

        return HttpResponse(etree.tostring(data_xml), mimetype='text/xml; charset=utf-8')

class PNGNodeResponseMixin(object):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        data = self.node.get_format('png')
        img_buffer = StringIO.StringIO()
        pylab.imsave(img_buffer, data.data, format='png')
        return HttpResponse(img_buffer.getvalue(), mimetype='image/png')

class BinaryNodeResponseMixin(object):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        #response = HttpResponse(mimetype='application/octet-stream')
        response = HttpResponse(mimetype="text/plain; charset=x-user-defined")
        # TODO: make this available through HTTP query or settings.
        # error_threshold = 1.e-3

        # TODO: do  we want a  consistency check that checks  the node
        # dimension info matches the dimensionality of the data?
        
        # TODO: we  assume dim  can be  parameterised, this  should be
        # generalised (e.g. if cannot  be paramterised, put in message
        # body)

        param_dim = self.node.parameterised_dim()
        
        response['X-H1DS-ndim'] = param_dim['ndim']
        for d in xrange(param_dim['ndim']):
            for k,v in param_dim[d].iteritems():
                response['X-H1DS-dim-{}-{}'.format(d,k)] = v

        requested_dtype = request.GET.get('bin_assert_dtype', None)
        if requested_dtype != None:
            try:
                requested_dtype = getattr(np, requested_dtype)
            except AttributeError:
                requested_dtype = None
                
        discretised_data = self.node.discretised_data(assert_dtype=requested_dtype)
        response.write(discretised_data['data'].tostring())
        response['X-H1DS-data-min'] = discretised_data['min']
        response['X-H1DS-data-delta'] = discretised_data['delta']
        response['X-H1DS-data-rmserr'] = discretised_data['rms_err']
        response['X-H1DS-data-dtype'] = discretised_data['data'].dtype.name
        response['X-H1DS-data-shape'] = ",".join(str(i) for i in discretised_data['data'].shape)
        
    
        # For data, if requested, quantize with requested bitlength
        # X-H1DS-data-quantised: True or False
        ## if quantised, give error value.
        
        #disc_data = self.node.get_format('bin')
        #response = HttpResponse(disc_data['iarr'].tostring(), mimetype='application/octet-stream') ## use response.write()
        #response['X-H1DS-signal-min'] = disc_data['minarr']
        #response['X-H1DS-signal-delta'] = disc_data['deltar']
        #response['X-H1DS-dim-t0'] = self.node.data.dim[0]
        #response['X-H1DS-dim-delta'] = self.node.data.dim[1]-self.node.data.dim[0]
        #response['X-H1DS-dim-length'] = len(self.node.data.dim)
        #response['X-H1DS-signal-units'] = self.node.data.units
        #response['X-H1DS-signal-dtype'] = str(disc_data['iarr'].dtype)
        #response['X-H1DS-dim-units'] = self.node.data.dim_units
        return response

    
class HTMLNodeResponseMixin(object):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        # get any saved signals for the user
        if request.user.is_authenticated():
            user_signals = UserSignal.objects.filter(user=request.user)
            user_signal_form = UserSignalForm()
        else:
            user_signals = []
            user_signal_form = None            
        html_metadata = {
            'tree':self.node.url_processor.tree,
            'shot':self.node.url_processor.shot, 
            #'user_signals':user_signals,
            #'node_display_info':self.node.get_display_info(),
            }
        
        if self.node.get_data() == None:
            template = "node_nodata.html"
        elif np.isscalar(self.node.get_data()):
            template = "node_scalar.html"
        elif 1 <= len(self.node.get_data().shape) <= 3:
            template = "node_{}d.html".format(len(self.node.get_data().shape))
        else:
            template = "node_unknown_data.html"
        x = get_trees()
        trees = {'current':self.node.url_processor.tree}
        trees['other'] = [t for t in get_trees() if t.lower() != trees['current'].lower()]
        trees['all'] = sorted(get_trees())
        alt_formats = ['json', 'png', 'xml', 'csv', 'bin']
        return render_to_response('h1ds_core/{}'.format(template), 
                                  {#'node_content':self.node.get_format('html'),
                                   #'html_metadata':html_metadata,
                                   'user_signals':user_signals,
                                   'user_signal_form':user_signal_form,
                                   'node':self.node,
                                   'trees':trees,
                                   'alt_formats':alt_formats,
                                   'is_debug':str(settings.DEBUG),
                                   'request_fullpath':request.get_full_path()},
                                  context_instance=RequestContext(request))

class MultiNodeResponseMixin(HTMLNodeResponseMixin, JSONNodeResponseMixin,
                             PNGNodeResponseMixin, XMLNodeResponseMixin,
                             BinaryNodeResponseMixin, CSVNodeResponseMixin):
    """Dispatch to requested representation."""

    representations = {
        "html":HTMLNodeResponseMixin,
        "json":JSONNodeResponseMixin,
        "png":PNGNodeResponseMixin,
        "xml":XMLNodeResponseMixin,
        "bin":BinaryNodeResponseMixin,
        "csv":CSVNodeResponseMixin,
        }

    def dispatch(self, request, *args, **kwargs):
        # Try  to   dispatch  to   the  right  method   for  requested
        # representation;  if a  method  doesn't exist,  defer to  the
        # error  handler.  Also  defer  to the  error  handler if  the
        # request method isn't on the approved list.
        
        # TODO: for now, we only support GET and POST, as we are using
        # the query string to determing which representation should be
        # used,  and  the querydict  is  only  available for  GET  and
        # POST. Need  to bone  up on whether  query strings  even make
        # sense  on other  HTTP verbs.  Probably, we  should use  HTTP
        # headers to figure out which  content type should be returned
        # - also,  we might  be able  to support  both URI  and header
        # based content type selection.
        # http://stackoverflow.com/questions/381568/rest-content-type-should-it-be-based-on-extension-or-accept-header
        # http://www.xml.com/pub/a/2004/08/11/rest.html

        if request.method == 'GET':
            requested_representation = get_format(request).lower()
        elif request.method == 'POST':
            requested_representation = gte_format(request)
        else:
            # until we figure out how to determine appropriate content type
            return self.http_method_not_allowed(request, *args, **kwargs)

        if not requested_representation in self.representations:
            # TODO: should handle this and let user know? rather than ignore?
            requested_representation = 'html'

        self.url_processor = URLProcessor(url=self.kwargs['url'])
        #data_interface = DataInterface(self.url_processor)
        #self.node = data_interface.get_node()
        self.node = Node(url_processor = self.url_processor)
        self.node.apply_filters(request=request)
        
        rep_class = self.representations[requested_representation]

        if request.method.lower() in rep_class.http_method_names:
            handler = getattr(rep_class, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        self.request = request
        self.args = args
        self.kwargs = kwargs
        return handler(self, request, *args, **kwargs)


class NodeView(MultiNodeResponseMixin, View):
    pass
