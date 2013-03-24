import inspect
import re
import xml.etree.ElementTree as etree

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.core import serializers
from django.http import HttpResponse
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

data_module = import_module(settings.H1DS_DATA_MODULE)
URLProcessor = getattr(data_module, 'URLProcessor')


def get_latest_shot_function():
    i = settings.LATEST_SHOT_FUNCTION.rfind('.')
    module, attr = settings.LATEST_SHOT_FUNCTION[:i], settings.LATEST_SHOT_FUNCTION[i+1:]
    try:
        mod = import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured('Error importing request processor module %s: "%s"' % (module, e))
    try:
        func  = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" callable request processor' % (module, attr))
    return func

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
import h1ds_mdsplus.filters as df
############

# Match strings "f(fid)_name", where fid is the filter ID
filter_name_regex = re.compile('^f(?P<fid>\d+?)_name')

# Match strings "f(fid)_arg(arg number)", where fid is the filter ID
filter_arg_regex = re.compile('^f(?P<fid>\d+?)_arg(?P<argn>\d+)')

# Match strings "f(fid)_kwarg_(arg name)", where fid is the filter ID
filter_kwarg_regex = re.compile('^f(?P<fid>\d+?)_kwarg_(?P<kwarg>.+)')


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

def get_filter_list(request):
    """Parse GET query sring and return sorted list of filter names.

    Arguments:
    request -- a HttpRequest instance with HTTP GET parameters.
    
    """
    filter_list = []

    if not request.method == 'GET':
        # If the HTTP method is not GET, return an empty list.
        return filter_list

    # First, create a dictionary with filter numbers as keys:
    # e.g. {1:{'name':filter, 'args':{1:arg1, 2:arg2, ...}, kwargs:{}}
    # note  that the  args  are stored  in  a dictionary  at this  point
    # because we cannot assume GET query will be ordered.
    filter_dict = {}
    for key, value in request.GET.iteritems():
        
        name_match = filter_name_regex.match(key)
        if name_match != None:
            fid = int(name_match.groups()[0])
            if not filter_dict.has_key(fid):
                filter_dict[fid] = {'name':"", 'args':{}, 'kwargs':{}}
            filter_dict[fid]['name'] = value
            continue

        arg_match = filter_arg_regex.match(key)
        if arg_match != None:
            fid = int(arg_match.groups()[0])
            argn = int(arg_match.groups()[1])
            if not filter_dict.has_key(fid):
                filter_dict[fid] = {'name':"", 'args':{}, 'kwargs':{}}
            filter_dict[fid]['args'][argn] = value
            continue

        kwarg_match = filter_kwarg_regex.match(key)
        if kwarg_match != None:
            fid = int(arg_match.groups()[0])
            kwarg = arg_match.groups()[1]
            if not filter_dict.has_key(fid):
                filter_dict[fid] = {'name':"", 'args':{}, 'kwargs':{}}
            filter_dict[fid]['kwargs'][kwarg] = value
            continue
    
    for fid, filter_data in sorted(filter_dict.items()):
        arg_list = [i[1] for i in sorted(filter_data['args'].items())]
        filter_list.append([fid, filter_data['name'], arg_list, filter_data['kwargs']])
                           
    return filter_list

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
        filter_function = getattr(df, filter_name)

        # We'll append the filter to this path and redirect there.
        return_path = qdict.pop('path')[-1]

        if overwrite_fid:
            fid = int(qdict.pop('fid')[-1])
            for k,v in qdict.items():
                if k.startswith('f%d_' %fid):
                    qdict.pop(k)
        else:
            # Find the maximum fid in the existing query and +1
            fid = get_max_fid(self.request)+1

        # We expect the filter arguments to be passed as key&value in the HTTP query.
        filter_arg_names = inspect.getargspec(filter_function).args[1:]
        filter_arg_values = [qdict.pop(a)[-1] for a in filter_arg_names]

        # add new filter to query dict
        qdict.update({'f%d_name' %(fid):filter_name})
        for argn, arg_val in enumerate(filter_arg_values):
            qdict.update({'f%d_arg%d' %(fid,argn):arg_val})

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
            if k.startswith('f%d_' %filter_id):
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
        input_shot = shot_regex.findall(input_path)[0]
        new_url = input_path.replace("/"+str(input_shot)+"/", "/"+str(shot)+"/")
        output_json = '{"new_url":"%s"}' %new_url
        return HttpResponse(output_json, 'application/javascript')

def xml_latest_shot(request):
    """Hack to get IDL client working again - this should be merged with other latest shot view"""
    
    shot = str(get_latest_shot())
    response_xml = etree.Element('{http://h1svr.anu.edu.au/mdsplus}mdsurlmap',
                             attrib={'{http://www.w3.org/XML/1998/namespace}lang': 'en'})
    
    shot_number = etree.SubElement(response_xml, 'shot_number', attrib={})
    shot_number.text = shot
    return HttpResponse(etree.tostring(response_xml), mimetype='text/xml; charset=utf-8')

class AJAXLatestShotView(View):
    """Return latest shot."""
    
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        view = request.GET.get('view', 'json')
        if view.lower() == 'xml':
            return xml_latest_shot(request)
        latest_shot = get_latest_shot()
        return HttpResponse('{"latest_shot":"%s"}' %latest_shot, 'application/javascript')

def request_url(request):
    """Return the URL for the requested parameters."""

    shot = request.GET['shot']
    path = request.GET['path']
    tree = request.GET['tree']

    
    url_xml = etree.Element('{http://h1svr.anu.edu.au/}mdsurlmap',
                             attrib={'{http://www.w3.org/XML/1998/namespace}lang': 'en'})
    
    # add mds info
    shot_number = etree.SubElement(url_xml, 'shot_number', attrib={})
    shot_number.text = shot
    mds_path = etree.SubElement(url_xml, 'path', attrib={})
    mds_path.text = path
    mds_tree = etree.SubElement(url_xml, 'tree', attrib={})
    mds_tree.text = tree

    url_processor = URLProcessor(shot=int(shot), tree=tree, path=path)
    url = url_processor.get_url()
    url_el = etree.SubElement(url_xml, 'url', attrib={})
    url_el.text = url

    return HttpResponse(etree.tostring(url_xml), mimetype='text/xml; charset=utf-8')


class Node(object):
    pass

class NodeView(View):
    pass
    
