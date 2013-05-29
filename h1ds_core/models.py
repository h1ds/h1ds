"""Model classes for h1ds_core

H1DS Core contains models for communicating between H1DS modules.


"""
import inspect
import re
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.forms import ModelForm
from django.utils.importlib import import_module
from django.template.defaultfilters import slugify

from python_field.fields import PythonCodeField
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager

from h1ds_core.filters import BaseFilter, excluded_filters

if hasattr(settings, "WORKSHEETS_PUBLIC_BY_DEFAULT"):
    public_worksheets_default = settings.WORKSHEETS_PUBLIC_BY_DEFAULT
else:
    public_worksheets_default = False

# Match strings "f(fid)_name", where fid is the filter ID
filter_name_regex = re.compile('^f(?P<fid>\d+?)')

# Match strings "f(fid)_kwarg_(arg name)", where fid is the filter ID
filter_kwarg_regex = re.compile('^f(?P<fid>\d+?)_(?P<kwarg>.+)')
    
backend_module = import_module(settings.H1DS_BACKEND)

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
        kwarg_match = filter_kwarg_regex.match(key)
        if kwarg_match != None:
            fid = int(kwarg_match.groups()[0])
            kwarg = kwarg_match.groups()[1]
            if not filter_dict.has_key(fid):
                filter_dict[fid] = {'name':"", 'kwargs':{}}
            filter_dict[fid]['kwargs'][kwarg] = value
            continue
        
        name_match = filter_name_regex.match(key)
        if name_match != None:
            fid = int(name_match.groups()[0])
            if not filter_dict.has_key(fid):
                filter_dict[fid] = {'name':"", 'kwargs':{}}
            filter_dict[fid]['name'] = value
            continue
    
    for fid, filter_data in sorted(filter_dict.items()):
        filter_list.append([fid, filter_data['name'], filter_data['kwargs']])
                           
    return filter_list

def get_all_filters():
    """Get all filters from modules listed in settings.DATA_FILTER_MODULES."""
    filters = {}
    for filter_module_name in settings.DATA_FILTER_MODULES:
        mod = import_module(filter_module_name)
        mod_filters = [cl for name, cl in inspect.getmembers(mod) if
                       inspect.isclass(cl) and issubclass(cl, BaseFilter) and
                       not cl in excluded_filters]
        filters.update((f.get_slug(), f) for f in mod_filters)
    return filters

class FilterManager(object):
    """Get available filters for given data.

    FilterManager caches lookups to avoid repeated checks of filters for
    available datatypes.
    """
    def __init__(self):
        self.filters = get_all_filters()
        self.cache = {}

    def get_filters(self, data):
        """Get available processing filters for data object provided."""
        ndim = data.ndim if hasattr(data, "ndim") else 0
        if ndim == 0:
            _dt = type(data)
        else:
            _dt = data.dtype
        data_type = (ndim, _dt)
        if not self.cache.has_key(data_type):
            data_filters = {}
            for fname, filter_ in self.filters.iteritems():
                if filter_.is_filterable(data):
                    data_filters[fname] = filter_
            self.cache[data_type] = data_filters
        return self.cache[data_type]

filter_manager = FilterManager()

class Node(MPTTModel, backend_module.NodeData):
    """Node of a data tree.

    A single data tree represents one shot.
    The root node has path = str(shot_number).
    """
    #shot = models.PositiveIntegerField()
    path = models.CharField(max_length=256)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    slug = models.SlugField()
    has_data = models.BooleanField(default=True)
    dimension = models.PositiveSmallIntegerField(blank=True, null=True)
    dtype = models.CharField(max_length=16)

    
    data = None
    dim = None
    labels = None
    primary_data = None
    primary_dim = None
    primary_labels = None
    filter_history = []
    
    # TODO: rename so that path, nodepath are intuitive
    def _get_node_path(self):
        ancestry = self.get_ancestors(include_self=True)
        return "/".join([n.path for n in ancestry])
        
    nodepath = property(_get_node_path)

    # I'm not sure  why we need to  do this explicitly, but  if we don't
    # then .objects becomes DataTreeManager()
    objects = TreeManager()
    datatree = backend_module.DataTreeManager()

    def get_absolute_url(self):
        return reverse('node-detail', kwargs={'nodepath':self.nodepath})
    
    def get_available_filters(self):
        return filter_manager.get_filters(self.data)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.path)
        super(Node, self).save(*args, **kwargs)
    
    def __unicode__(self):
        ancestry = self.get_ancestors(include_self=True)
        unicode_val = unicode(ancestry[0].path)
        if len(ancestry)>1:
            unicode_val += unicode(":")
            unicode_val += u'\u2192'.join(
                [unicode(n.path) for n in ancestry[1:]])
        return unicode_val

    def get_shot(self):
        if self.level==0:
            shot = int(self.path)
        else:
            root_node = self.get_root()
            shot = int(root_node.path)
        return shot

    def get_node_for_shot(self,shot_number):
        """Get same node in different shot tree, if it exists."""

        node_ancestry = [i.slug for i in self.get_ancestors(include_self=True)]
        node_ancestry[0] = str(shot_number)
        return Node.datatree.get_node_from_ancestry(node_ancestry)

    def get_node_for_previous_shot(self):
        previous_shot = self.get_shot()-1
        return self.get_node_for_shot(previous_shot)

    def get_node_for_next_shot(self):
        next_shot = self.get_shot()+1
        return self.get_node_for_shot(next_shot)

    
    def populate_child_nodes(self):
        """Use primary data source to populate child nodes."""

        child_names = self.get_child_names_from_primary_source()
        for child in child_names:
            node = Node(path=child, parent=self)
            # TODO: can we delay the save and write in bulk?
            node.save()
            node.populate_child_nodes()

    def apply_filters(self, request):
        if self.primary_data == None:
            self.primary_data = self.read_primary_data()
        if self.primary_dim == None:
            self.primary_dim = self.read_primary_dim()
        if self.primary_labels == None:
            self.primary_labels = self.read_primary_labels()
            
        # reset data as primary data
        self.data = self.primary_data
        self.dim = self.primary_dim
        self.labels = self.primary_labels
        for fid, name, kwargs in get_filter_list(request):
            self.apply_filter(fid, name, **kwargs)
        
    def preprocess_filter_kwargs(self, kwargs):
        # TODO: should filters.http_arg be put here instead?
        for key, val in kwargs.iteritems():
            if isinstance(val, str) and "__shot__" in val:
                shot_str = str(self.url_processor.shot)
                kwargs[key] = val.replace("__shot__", shot_str)
        return kwargs

    def apply_filter(self, fid, name, **kwargs):
        # make sure data and dim can be accessed via node.data, node.dim... 
        #d = self.get_data()
        #dim = self.get_dim()
        #labels = self.get_labels()
        
        f_kwargs = self.preprocess_filter_kwargs(kwargs)
        #filter_class = filter_manager.filters[name](*f_args, **f_kwargs)
        filter_class = filter_manager.filters[name](**f_kwargs)
        filter_class.apply(self)
        
        #self.filter_history.append((fid, name, kwargs))
        self.filter_history.append((fid, filter_class, kwargs))
        #self.summary_dtype = sql_type_mapping.get(type(self.data))
        #self.available_filters = get_dtype_mappings(self.data)['filters']
        #self.available_views = get_dtype_mappings(self.data)['views'].keys()
            
class Filter(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField()
    code = PythonCodeField()
        

class H1DSSignal(models.Model):
    """Identifier for signals passed though the H1DS system."""
    name = models.CharField(max_length=50,
                            unique=True,
                            help_text="Name of signal")
    description = models.CharField(max_length=500,
                                   help_text="Description of signal")

    def natural_key(self):
        return (self.name,)

    def __unicode__(self):
        return unicode(self.name)

class H1DSSignalInstance(models.Model):
    """Records an instance of an H1DS signal."""
    signal = models.ForeignKey(H1DSSignal)
    time = models.DateTimeField(auto_now_add=True)
    value = models.CharField(max_length=1024, blank=True)

    def __unicode__(self):
        return unicode("%s: %s" %(self.time, self.signal))
    
    class Meta:
        ordering = ('-time',)
        get_latest_by = 'time'


class Pagelet(models.Model):
    name = models.CharField(max_length=1024)
    pagelet_type = models.CharField(max_length=128)
    url = models.URLField(max_length=2048)
        
class Worksheet(models.Model):
    """A page for users to organise and store content."""
    user = models.ForeignKey(User)
    name = models.CharField(max_length=256)
    description = models.TextField()
    slug = models.SlugField(max_length=256)
    is_public = models.BooleanField(default=public_worksheets_default)
    pagelets = models.ManyToManyField(Pagelet, through='PageletCoordinates')

    class Meta:
        unique_together = (("user", "slug"),)

    def __unicode__(self):
        return unicode("[%s] %s" %(self.user, self.name))

    def get_absolute_url(self):
        return reverse("h1ds-user-worksheet", kwargs={
            "username":self.user.username,
            "worksheet":self.slug})

class PageletCoordinates(models.Model):
    pagelet = models.ForeignKey(Pagelet)
    worksheet = models.ForeignKey(Worksheet)
    coordinates = models.CharField(max_length=128)

    def get_coordinates(self):
        pass
    
class UserSignal(models.Model):
    """Save data URLs for user."""

    # TODO: unique together user, name

    user = models.ForeignKey(User, editable=False)
    url = models.URLField(max_length=2048)
    name = models.CharField(max_length=1024)
    ordering = models.IntegerField(blank=True)
    is_fixed_to_shot = models.BooleanField(default=True)
    shot = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return unicode("%s" %(self.name))


class UserSignalForm(ModelForm):
    class Meta:
        model = UserSignal
        fields = ('name', 'is_fixed_to_shot',)
