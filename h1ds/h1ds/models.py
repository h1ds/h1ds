"""Model classes for h1ds

H1DS Core contains models for communicating between H1DS modules.


"""
import hashlib
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

from h1ds.filters import BaseFilter, excluded_filters
from h1ds.utils import get_backend_shot_manager

if hasattr(settings, "WORKSHEETS_PUBLIC_BY_DEFAULT"):
    public_worksheets_default = settings.WORKSHEETS_PUBLIC_BY_DEFAULT
else:
    public_worksheets_default = False

# Match strings "f(fid)_name", where fid is the filter ID
filter_name_regex = re.compile('^f(?P<fid>\d+)')

# Match strings "f(fid)_kwarg_(arg name)", where fid is the filter ID
filter_kwarg_regex = re.compile('^f(?P<fid>\d+)_(?P<kwarg>.+)')
    
backend_module = import_module(settings.H1DS_DATA_BACKEND)

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

        data_type = (data.get_n_dimensions(), data.value_dtype)
        if not self.cache.has_key(data_type):
            data_filters = {}
            for fname, filter_ in self.filters.iteritems():
                if filter_.is_filterable(data):
                    data_filters[fname] = filter_
            self.cache[data_type] = data_filters
        return self.cache[data_type]

class Shot(models.Model):
    number = models.PositiveIntegerField(primary_key=True)
    timestamp = models.DateTimeField()
    
    objects = models.Manager()
    backend = get_backend_shot_manager()()

    def _get_root_nodes(self):
        return Node.objects.filter(level=0, shot=self)

    root_nodes = property(_get_root_nodes)

    def get_absolute_url(self):
        return reverse('shot-detail', kwargs={'shot':self.number})

    def save(self, *args, **kwargs):
        self.timestamp = Shot.backend.get_timestamp_for_shot(self.number)
        super(Shot, self).save(*args, **kwargs)
        self._populate()

    def _populate(self):
        for tree in Node.datatree.get_trees():
            node = Node(path=tree, shot=self)
            node.save()
            node.populate_child_nodes()

        
filter_manager = FilterManager()

class Node(MPTTModel, backend_module.NodeData):
    """Node of a data tree.

    A single data tree represents one shot.
    The root node has path = str(shot_number).
    """

    def __init__(self, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        self.filter_history = []

    # While it may be overkill to link to a shot for every node in the
    # tree, it allows  us to more easily search  nodes irrespective of
    # their tree  - for  example if we  want to find  all data  with a
    # specific dtype in  a range of shots, then we  don't want to have
    # to first  find the  tree from  the shot  number and  then search
    # nodes...
    # Previously, the  shot number was  stored only for the  root tree
    # node, but the code to find the  shot for a given node was rather
    # cumbersome.
    shot = models.ForeignKey(Shot)
    
    path = models.CharField(max_length=256)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    slug = models.SlugField()
    has_data = models.BooleanField(default=True)
    n_dimensions = models.PositiveSmallIntegerField(blank=True, null=True)
    dtype = models.CharField(max_length=16, blank=True)
    n_channels = models.PositiveSmallIntegerField(blank=True, null=True)

    # This is effectively a  fixed-length string unique identifier for
    # a  node, allowing  us  to find  the same  node  for other  shots
    # without needing to either search  the node ancestry or store the
    # (variable length,  possibly very long)  full tree path  for each
    # node. The  SHA1 is simply generated  from the full tree  path of
    # the node when the node is saved.
    path_checksum = models.CharField(max_length=40)
    
    ## TODO:
    ## have n_channels
    ## dtype, dimensions etc are lists with length n_channels
    ## same with original_data
    ## each element in n_channel original_data list has a Data instance
    ## data has dim, labels, name, units etc.
    ## for now, consider channels as indep, can later share info.
    
    primary_data = None
    #filtered_data = []
    #dim = None
    #labels = None
    #primary_data = None
    #primary_dim = None
    #primary_labels = None
    
    # TODO: rename so that path, nodepath are intuitive
    def _get_node_path(self):
        ancestry = self.get_ancestors(include_self=True)
        return "/".join([n.slug for n in ancestry])
        
    nodepath = property(_get_node_path)

    # I'm not sure  why we need to  do this explicitly, but  if we don't
    # then .objects becomes DataTreeManager()
    objects = TreeManager()
    datatree = backend_module.DataTreeManager()

    def get_data(self):
        if not hasattr(self, 'data'):
            self.primary_data = self.read_primary_data()
            self.data = self.primary_data
        return self.data
                
    def get_absolute_url(self):
        return reverse('node-detail', kwargs={'nodepath':self.nodepath, 'shot':self.shot.number})
    
    def get_available_filters(self):
        return filter_manager.get_filters(self.data)

    def _get_sha1(self):
        nodepath = self._get_node_path()
        return hashlib.sha1(nodepath).hexdigest()
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.path)
        super(Node, self).save(*args, **kwargs)
        # TODO: only single channel...
        self.primary_data = self.read_primary_data()
        if not self.primary_data:
            self.has_data = False
        else:
            self.has_data = True
            self.n_dimensions = self.primary_data.get_n_dimensions()
            self.dtype = self.primary_data.value_dtype
            self.n_channels = len(self.primary_data.value)
            
        self.path_checksum = self._get_sha1()
        super(Node, self).save()#update_fields=['path_checksum'])
        # TODO: if the node name changes then we also need to regenerate
        # sha1 keys for all descendents...
    
    def __unicode__(self):
        ancestry = self.get_ancestors(include_self=True)
        unicode_val = unicode(ancestry[0].path)
        if len(ancestry)>1:
            unicode_val += unicode(":")
            unicode_val += u'\u2192'.join(
                [unicode(n.path) for n in ancestry[1:]])
        return unicode_val

    ## def get_shot(self):
    ##     if self.level==0:
    ##         shot = int(self.path)
    ##     else:
    ##         root_node = self.get_root()
    ##         shot = int(root_node.path)
    ##     return shot

    def get_node_for_shot(self,shot_number):
        """Get same node in different shot tree, if it exists."""

        node_ancestry = [i.slug for i in self.get_ancestors(include_self=True)]
        node_ancestry[0] = str(shot_number)
        return Node.datatree.get_node_from_ancestry(node_ancestry)

    def get_node_for_previous_shot(self):
        previous_shot = Shot.backend.get_previous_shot_number(self.shot.number)
        return self.get_node_for_shot(previous_shot)

    def get_node_for_next_shot(self):
        next_shot = Shot.backend.get_next_shot_number(self.shot.number)
        return self.get_node_for_shot(next_shot)

    
    def populate_child_nodes(self):
        """Use primary data source to populate child nodes."""

        child_names = self.get_child_names_from_primary_source()
        for child in child_names:
            node = Node(path=child, parent=self, shot=self.shot)
            # TODO: can we delay the save and write in bulk?
            node.save()
            node.populate_child_nodes()

    def apply_filters(self, request):
        self.get_data()
        #if self.primary_data == None:
        #    self.primary_data = self.read_primary_data()
        #if self.primary_dim == None:
        #    self.primary_dim = self.read_primary_dim()
        #if self.primary_labels == None:
        #    self.primary_labels = self.read_primary_labels()
            
        # reset data as primary data
        #self.data = self.primary_data
        #self.dim = self.primary_dim
        #self.labels = self.primary_labels
        for fid, name, kwargs in get_filter_list(request):
            self.apply_filter(fid, name, **kwargs)

    def get_alternative_format_urls(self, request, alternative_formats):
        # alternative_formats = ['json', 'xml', etc...]
        self.alternative_format_urls = {}
        query_dict = request.GET.copy()
        try:
            query_dict.pop('format')
        except KeyError:
            pass
        for fmt in alternative_formats:
            query_dict.update({'format':fmt})
            self.alternative_format_urls[fmt] = request.build_absolute_uri(request.path)+"?"+query_dict.urlencode()
            query_dict.pop('format')
        
        
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
            
class FilterDtype(models.Model):

    name = models.CharField(max_length=128)
    code = PythonCodeField()
    def __unicode__(self):
        return unicode(self.name)

class FilterDim(models.Model):
    name = models.CharField(max_length=128)
    code = PythonCodeField()
    def __unicode__(self):
        return unicode(self.name)
        
class Filter(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField()
    data_dim = models.ManyToManyField(FilterDim)
    data_type = models.ManyToManyField(FilterDtype)
    code = PythonCodeField()

    def __unicode__(self):
        return unicode(self.name)

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
    slug = models.SlugField()
    is_public = models.BooleanField(default=public_worksheets_default)
    pagelets = models.ManyToManyField(Pagelet, through='PageletCoordinates')

    ## This causes  problems w/ MySQL,  maybe we just append  numbers to
    ## slugs when they're generated during save.
    #class Meta:
    #    unique_together = (("user", "slug"),)

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
