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

from h1ds import tasks
from h1ds.filters import BaseFilter, excluded_filters
from h1ds.utils import get_backend_shot_manager_for_device

if hasattr(settings, "WORKSHEETS_PUBLIC_BY_DEFAULT"):
    public_worksheets_default = settings.WORKSHEETS_PUBLIC_BY_DEFAULT
else:
    public_worksheets_default = False

# Match strings "f(fid)_name", where fid is the filter ID
filter_name_regex = re.compile('^f(?P<fid>\d+)')

# Match strings "f(fid)_kwarg_(arg name)", where fid is the filter ID
filter_kwarg_regex = re.compile('^f(?P<fid>\d+)_(?P<kwarg>.+)')


def get_data_backend_choices():
    return sorted((key, value['name']) for key, value in settings.DATA_BACKENDS.iteritems())


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
        if kwarg_match is not None:
            fid = int(kwarg_match.groups()[0])
            kwarg = kwarg_match.groups()[1]
            if not fid in filter_dict:
                filter_dict[fid] = {'name': "", 'kwargs': {}}
            filter_dict[fid]['kwargs'][kwarg] = value
            continue

        name_match = filter_name_regex.match(key)
        if name_match is not None:
            fid = int(name_match.groups()[0])
            if not filter_dict.has_key(fid):
                filter_dict[fid] = {'name': "", 'kwargs': {}}
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

    def get_filters_for_subtree(self, subtree):
        """Get available processing filters for data object provided."""
        return self.get_filters(subtree.n_dimensions, subtree.dtype)

    def get_filters(self, n_dimensions, dtype):
        data_type = (n_dimensions, dtype)
        if not data_type in self.cache:
            data_filters = {}
            for fname, filter_ in self.filters.iteritems():
                if filter_.is_filterable(n_dimensions=n_dimensions, dtype=dtype):
                    data_filters[fname] = filter_
            self.cache[data_type] = data_filters
        return self.cache[data_type]


class Device(models.Model):
    """Representation of an experimental device with its own data set."""

    def __init__(self, *args, **kwarg):
        super(Device, self).__init__(*args, **kwarg)
        self.backend_module = None

    name = models.CharField(max_length=32)
    description = models.TextField()
    slug = models.SlugField()
    # Using "+" for related_name tells Django not to create a backwards relation.
    # In this case, we don't want a backwards relation as it would clash with Shot.device.
    # We set null=True so that we can set up devices before we have shots and datasets set up.
    # TODO: restrict this foreign key to shots which belong to the device instance. This has been
    # done for the admin form, but should be done in general. The obvious approach would be to use
    # the limit_choices_to kwarg, but I can't see how to include the Device instance with that.
    latest_shot = models.ForeignKey("Shot", null=True, blank=True, related_name="+", on_delete=models.SET_NULL)

    is_default = models.BooleanField(default=True, help_text="Set this as the default device.")

    is_public = models.BooleanField(default=True,
                                    help_text="If true, the device will be visible to all users, and the general public.")

    # TODO: We should just use the django permissions API...
    allowed_users = models.ManyToManyField(User, blank=True, help_text="Users who can access this device if it is not public")

    # data backend for device is used to get shot timestamp.
    data_backend = models.CharField(max_length=4, choices=get_data_backend_choices(), default=settings.DEFAULT_DATA_BACKEND)

    read_only = models.BooleanField(default=True, help_text='If read only, then H1DS will not allow writing back to the primary database.')

    def user_is_allowed(self, user):
        is_allowed = self.is_public or self.allowed_users.filter(pk=user.pk)
        return is_allowed

    def get_absolute_url(self):
        return reverse("device-detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Device, self).save(*args, **kwargs)
        if self.is_default:
            for device in Device.objects.exclude(pk=self.pk).filter(is_default=True):
                device.is_default = False
                device.save()

    def get_backend_module(self):
        if not self.backend_module:
            module_name = settings.DATA_BACKENDS[self.data_backend]['module']
            self.backend_module = import_module(module_name)
        return self.backend_module

    def __unicode__(self):
        return self.name

    def get_trees(self):
        try:
            return [t[0] for t in settings.DATA_TREES[self.slug]]
        except KeyError:
            return []

    def get_allowed_trees_for_user(self, user):
        if not self.user_is_allowed(user):
            return []
        return [tree for tree in Tree.objects.filter(device=self) if tree.user_is_allowed(user)]


class ShotRange(models.Model):
    min_shot = models.IntegerField(null=True, blank=True)
    max_shot = models.IntegerField(null=True, blank=True)

    def is_number_in_range(self, number):
        if self.min_shot is None and self.max_shot is None:
            return True
        elif self.min_shot is None:
            if number <= self.max_shot:
                return True
        elif self.max_shot is None:
            if number >= self.min_shot:
                return True
        elif self.min_shot <= number <= self.max_shot:
            return True
        else:
            return False

    def __unicode__(self):
        return "{} - {}".format(self.min_shot, self.max_shot)


class Tree(models.Model):
    """Configuration for a data tree.

    """
    def __init__(self, *args, **kwarg):
        super(Tree, self).__init__(*args, **kwarg)
        self.backend_module = None

    name = models.CharField(max_length=64)
    slug = models.SlugField()
    device = models.ForeignKey(Device)
    configuration = models.TextField(blank=True)
    shot_ranges = models.ManyToManyField(ShotRange, blank=True)

    is_public = models.BooleanField(default=True,
                                    help_text="If true, the tree will be visible to all users, and the general public.")

    allowed_users = models.ManyToManyField(User, blank=True, help_text="Users who can access this tree if it is not public")

    # TODO: default should be the default for the device.
    data_backend = models.CharField(max_length=4, choices=get_data_backend_choices(), default=settings.DEFAULT_DATA_BACKEND)

    class Meta:
        unique_together = ("device", "slug")

    
    def user_is_allowed(self, user):
        is_allowed = self.is_public or self.allowed_users.filter(pk=user.pk)
        return is_allowed

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Tree, self).save(*args, **kwargs)
        backend_module = self.get_backend_module()
        backend_module.save_tree(self)

    def __unicode__(self):
        return self.slug

    def get_backend_module(self):
        if not self.backend_module:
            module_name = settings.DATA_BACKENDS[self.data_backend]['module']
            self.backend_module = import_module(module_name)
        return self.backend_module

    def add_shot(self, shot_number):
        shot_range, created = ShotRange.objects.get_or_create(min_shot=shot_number, max_shot=shot_number)
        self.shot_ranges.add(shot_range)
        # call self.consolidate_shot_ranges()
        pass

    def consolidate_shot_ranges(self):
        # TODO
        # if a pair of contiguous shot ranges exist, replace with single shot range.
        # remove old shot ranges if not used by other trees.
        pass
    
    def load(self):
        backend_module = self.get_backend_module()
        loader = backend_module.TreeLoader()
        loader.load(self)

    def get_fallback_root_nodes_for_shot(self, shot_number):
        #tree_root_node = Node.fallback.create_node(shot_number, self, '')
        #return tree_root_node.get_child_nodes(fallback=True)
        backend_module = self.get_backend_module()
        data_interface = backend_module.DataInterface(shot=shot_number, tree=self, path=[])
        return data_interface.get_child_nodes(fallback=True)

    def get_root_nodes_for_shot(self, shot_number):
        nodes_for_shot = Node.objects.filter(shot__number=shot_number)
        if nodes_for_shot.count() == 0:
            return self.get_fallback_root_nodes_for_shot(shot_number)
        else:
            return nodes_for_shot.filter(node_path__tree=self, node_path__parent__path=NodePath.TOP_PATH).exclude(node_path__path="").order_by('node_path__path')


class ShotFallbackManager(models.Manager):

    def create_shot(self, device, number):
        shot = self.model(number=number, device=device)
        shot.is_fallback = True
        shot.fallback_data = {'device': device,
                              'number': number}
        return shot


class Shot(models.Model):
    def __init__(self, *args, **kwargs):
        super(Shot, self).__init__(*args, **kwargs)
        self.is_fallback = False

    number = models.PositiveIntegerField(primary_key=True)
    timestamp = models.DateTimeField(blank=True)
    device = models.ForeignKey(Device)

    objects = models.Manager()
    #backend = get_backend_shot_manager(None)()
    fallback = ShotFallbackManager()


    def _get_root_pathmaps(self):
        return Node.objects.filter(shot=self, node_path__parent=None)

    def get_allowed_trees(self, user):
        allowed_trees = []
        for t in self.get_active_trees():
            if t.user_is_allowed(user):
                allowed_trees.append(t)
        return allowed_trees

    def get_active_trees(self):
        active_trees = []
        for tree in Tree.objects.filter(device=self.device):
            if tree.shot_ranges.count() == 0:
                active_trees.append(tree)
            else:
                is_active = False
                for shot_range in tree.shot_ranges:
                    if shot_range.is_number_in_range(self.number):
                        is_active = True
                if is_active:
                    active_trees.append(tree)
        return active_trees



    root_pathmaps = property(_get_root_pathmaps)

    def __unicode__(self):
        return unicode(self.number)

    def get_absolute_url(self):
        return reverse('shot-detail', kwargs={'device': self.device.slug, 'shot': self.number})

    def save(self, set_as_latest=False, populate_tree=True, *args, **kwargs):
        if not self.is_fallback:
            # TODO: don't set timestamp if it's already there.
            shot_manager = get_backend_shot_manager_for_device(self.device)
            self.timestamp = shot_manager().get_timestamp_for_shot(self.number)
            super(Shot, self).save(*args, **kwargs)
            if set_as_latest:
                self.set_as_latest_shot()
            if populate_tree:
                # need to set backend_module to None, as the model is not pickleable
                self.device.backend_module = None
                self.populate_tree()

            if not self.device.latest_shot:
                self.device.latest_shot = self
                self.device.save()

    def populate_tree(self):
        if self.is_fallback:
            return None
        # actually - we should set as latest shot straight away,
        # and have another parameter which keeps the state of tree cacheing.
        # TODO: what if shot is already populated?
        for tree in self.get_active_trees():
            # HACK: callback is a new task so we can use celery's task_sent signal when populate_tree is finished.
            # A better way would be to use a task_success signal, but I've had problems with specifying the sender
            # in signal.connect(), so currently we have this hack job using task_send.
            tasks.populate_tree.apply_async(args=[self, tree],
                                            link=tasks.populate_tree_success.s())


    def set_as_latest_shot(self, *args, **kwargs):
        # allow args, kwargs as this is being used as
        # callback to populate_tree - which may try to
        # populate this method with its output
        self.device.latest_shot = self
        self.device.save()


filter_manager = FilterManager()


class NodePath(models.Model):

    TOP_PATH = "__NODEPATH_TOP__"

    parent = models.ForeignKey('self', null=True, blank=True)
    # path component, as appears in url, except for tree..
    path = models.CharField(max_length=1024)
    tree = models.ForeignKey(Tree)
    # do we need hash anymore?
    #path_hash = models.CharField(max_length=40)
    nodes = models.ManyToManyField('SubTree', through='Node')

    class Meta:
        unique_together = ("path", "tree")

    # deprecated: use reverse lookup unstead
    #def get_fullpath(self):
    #    return "/".join([self.tree.slug, self.path])

    def __unicode__(self):
        return self.path

    def get_path_components(self):
        return self.path.split("/")

    def get_node_name(self):
        split_path = self.path.split("/")
        if len(split_path) > 0:
            return split_path[-1]
        else:
            return ""

class NodeFallbackManager(models.Manager):

    def create_node(self, shot_number, tree,nodepath):
        node = self.model()
        node.is_fallback = True
        node.fallback_data = {'tree': tree,
                              'shot_number': shot_number,
                              'nodepath': nodepath
                              }
        return node


class Node(models.Model):
    """Mapping of data sub-tree to a nodepath.

    Nodes can exist in fallback mode, which means they can present data from the
    primary data source but not be saved in the H1DS index.

    """
    def __init__(self, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        self.data_interface = None
        self.data = None
        self.filter_history = []
        self.is_fallback = False

    # we allow blank=True on foreign keys so we can generate fallback Node instances without touching the database.
    node_path = models.ForeignKey(NodePath, blank=True)
    subtree = models.ForeignKey('SubTree', blank=True)
    shot = models.ForeignKey(Shot, blank=True)

    objects = models.Manager()
    fallback = NodeFallbackManager()

    def __unicode__(self):
        return "{}: {}".format(self.shot.number, self.node_path.path)

    def save_data(self, data_instance):
        """Write data instance to data backend.

        TODO: refactor this into self.save()        
        """
        self.data = data_instance
        tree = self.get_tree()
        backend_module = tree.get_backend_module()
        backend_module.save_node(self)
    
    def save(self, *args, **kwargs):
        if not self.is_fallback:
            super(Node, self).save(*args, **kwargs)
            #self.save_data()

    def get_absolute_url(self):

        kwargs = {'device': self.get_device().slug,
                  'shot': self.get_shot_number(),
                  'tree': self.get_tree().slug}

        if self.get_nodepath() is NodePath.TOP_PATH:
            url_name = "tree-detail"
        else:
            url_name = "node-detail"
            kwargs['nodepath'] = self.get_nodepath()

        return reverse(url_name, kwargs=kwargs)

    def get_shot_number(self):
        """fallback aware shot number getter."""
        if self.is_fallback:
            return self.fallback_data['shot_number']
        else:
            return self.shot.number

    def get_tree(self):
        """Fallback aware tree getter."""
        if self.is_fallback:
            return self.fallback_data['tree']
        else:
            return self.node_path.tree

    def get_nodepath(self):
        if self.is_fallback:
            return self.fallback_data['nodepath']
        else:
            return self.node_path.path

    def get_path_components(self):
        """Fallback aware path component getter."""
        return self.get_nodepath().split('/')

    def get_data_interface(self):
        if self.data_interface is None:
            if self.is_fallback or (not self.is_fallback and self.subtree.has_data):
                tree = self.get_tree()
                backend_module = tree.get_backend_module()
                self.data_interface = backend_module.DataInterface(shot=self.get_shot_number(),
                                                                   tree=tree,
                                                                   path=self.get_path_components())
        return self.data_interface

    def get_device(self):
        """Fallback aware device getter."""
        if self.is_fallback:
            return self.fallback_data['tree'].device
        else:
            return self.shot.device

    def get_data(self):
        if self.data is None:
            if self.is_fallback or (not self.is_fallback and self.subtree.has_data):
                data_interface = self.get_data_interface()
                self.data = data_interface.read_primary_data()
        return self.data

    def get_available_filters(self):
        if not self.data:
            return None
        if self.is_fallback:
            return filter_manager.get_filters(self.data.get_n_dimensions(), self.data.value_dtype)
        else:
            return self.subtree.get_available_filters()

    def apply_filters(self, request):
        self.get_data()
        for fid, name, kwargs in get_filter_list(request):
            self.apply_filter(fid, name, **kwargs)

    def preprocess_filter_kwargs(self, kwargs):
        # TODO: should filters.http_arg be put here instead?
        for key, val in kwargs.iteritems():
            if isinstance(val, str) and "__shot__" in val:
                shot_str = str(self.shot.number)
                kwargs[key] = val.replace("__shot__", shot_str)
        return kwargs

    def apply_filter(self, fid, name, **kwargs):
        f_kwargs = self.preprocess_filter_kwargs(kwargs)
        filter_class = filter_manager.filters[name](**f_kwargs)
        filter_class.do_filter(self)
        self.filter_history.append((fid, filter_class, kwargs))

    def get_absolute_url_for_latest_shot(self):
        kwargs = {'device': self.get_device().slug,
                  'shot': 'latest',
                  'tree': self.get_tree().slug}

        if self.get_nodepath() is NodePath.TOP_PATH:
            url_name = "tree-detail"
        else:
            url_name = "node-detail"
            kwargs['nodepath'] = self.get_nodepath()

        return reverse(url_name, kwargs=kwargs)

    def get_node_for_shot(self, shot_number):
        """Get same node in different shot tree, if it exists."""

        return Node.objects.get(node_path=self.node_path,
                                shot__number=shot_number)

    def get_node_for_previous_shot(self):
        # TODO: want users to be able to distinguish between cached and fallback shots
        #previous_shot = Shot.backend.get_previous_shot_number(self.shot.number)
        #return self.get_node_for_shot(previous_shot)
        return self.get_node_for_shot(self.shot.number-1)

    def get_node_for_next_shot(self):
        # TODO: want users to be able to distinguish between cached and fallback shots
        #next_shot = Shot.backend.get_next_shot_number(self.shot.number)
        #return self.get_node_for_shot(next_shot)
        return self.get_node_for_shot(self.shot.number+1)

    def get_parent(self):
        if self.is_fallback:
            node_path_components = self.get_path_components()
            if len(node_path_components) <= 1:
                return None
            else:
                parent_path = '/'.join(node_path_components[:-1])
                node = Node.fallback.create_node(shot_number=self.get_shot_number(),
                                                 tree=self.get_tree(),
                                                 nodepath=parent_path
                                                 )
                return node
        try:
            return Node.objects.get(node_path=self.node_path.parent, shot=self.shot)
        except Node.DoesNotExist:
            return None

    def get_ancestors(self, include_self=False):
        parent = self.get_parent()
        if parent:
            ancestors = parent.get_ancestors(include_self=True)
        else:
            ancestors = []
        if include_self:
            ancestors.append(self)
        return ancestors

    def get_children(self):
        if self.is_fallback:
            if not self.data_interface or not self.data:
                return []
            child_nodes = self.data_interface.get_child_nodes(fallback=True)
            return sorted(child_nodes, key=lambda x: x.get_nodepath())
        else:
            return Node.objects.filter(node_path__parent=self.node_path, shot=self.shot).order_by('node_path__path')

    def get_node_name(self):
        path_components = self.get_path_components()
        try:
            return path_components[-1]
        except IndexError:
            return ''

class SubTree(models.Model):
    """Node of a data tree.

    """

    def __init__(self, *args, **kwargs):
        super(SubTree, self).__init__(*args, **kwargs)
        self.filter_history = []

    #shots = models.ManyToManyField(Shot)

    #path = models.CharField(max_length=256)
    children = models.ManyToManyField('self')
    #slug = models.SlugField()
    has_data = models.BooleanField(default=True)
    n_dimensions = models.PositiveSmallIntegerField(blank=True, null=True)
    dtype = models.CharField(max_length=16, blank=True)
    n_channels = models.PositiveSmallIntegerField(blank=True, null=True)

    subtree_hash = models.CharField(max_length=40, unique=True)

    # This is effectively a  fixed-length string unique identifier for
    # a  node, allowing  us  to find  the same  node  for other  shots
    # without needing to either search  the node ancestry or store the
    # (variable length,  possibly very long)  full tree path  for each
    # node. The  SHA1 is simply generated  from the full tree  path of
    # the node when the node is saved.
    #path_checksum = models.CharField(max_length=40)

    ## TODO:
    ## have n_channels
    ## dtype, dimensions etc are lists with length n_channels
    ## same with original_data
    ## each element in n_channel original_data list has a Data instance
    ## data has dim, labels, name, units etc.
    ## for now, consider channels as indep, can later share info.

    primary_data = None

    #def get_ancestors(self, include_self=False):
    #    if self.parent:
    #        ancestors = self.parent.get_ancestors(include_self=True)
    #    else:
    #        ancestors = []
    #    if include_self:
    #        ancestors.append(self)
    #    return ancestors

    ## TODO: rename so that path, nodepath are intuitive
    #def _get_node_path(self):
    #    ancestry = self.get_ancestors(include_self=True)
    #    return "/".join([n.slug for n in ancestry])

    #nodepath = property(_get_node_path)

    def get_data(self):
        if not hasattr(self, 'data'):
            self.primary_data = self.read_primary_data()
            self.data = self.primary_data
        return self.data

    def get_absolute_url(self, use_latest_shot=False):
        if use_latest_shot:
            shot = 'latest'
        else:
            shot = self.shot.number
        return reverse('node-detail', kwargs={'device': self.shot.device, 'nodepath': self.nodepath, 'shot': shot})

    def get_absolute_url_for_latest_shot(self):
        return self.get_absolute_url(use_latest_shot=True)

    def get_available_filters(self):
        return filter_manager.get_filters_for_subtree(self)

    def _get_sha1(self):
        nodepath = self._get_node_path()
        return hashlib.sha1(nodepath).hexdigest()

    #def save(self, *args, **kwargs):
    #    self.slug = slugify(self.path)
    #    for child in self.get_child_nodes():
    #        self.children.add(child)
    #
    #    #super(Node, self).save(*args, **kwargs)
    #    # TODO: only single channel...
    #    self.primary_data = self.read_primary_data()
    #    if not self.primary_data:
    #        self.has_data = False
    #    else:
    #        self.has_data = True
    #        self.n_dimensions = self.primary_data.get_n_dimensions()
    #        self.dtype = self.primary_data.value_dtype
    #        # TODO: shouldn't need try/except here
    #        try:
    #            self.n_channels = len(self.primary_data.value)
    #        except (AttributeError, TypeError):
    #            self.n_channels = 0
    #
    #    self.path_checksum = self._get_sha1()
    #    self.subtree_hash = self.generate_subtree_hash()
    #    super(Node, self).save()  # update_fields=['path_checksum'])
    #    # TODO: if the node name changes then we also need to regenerate
    #    # sha1 keys for all descendents...

    
    def generate_subtree_hash(self):
        hash_fields = ('has_data', 'n_dimensions', 'dtype', 'n_channels')
        hash_val = ""
        for field in hash_fields:
            hash_val += hashlib.sha1(unicode(getattr(self, field))).hexdigest()
        for child in self.children.all():
            # can we access children before model is saved?
            hash_val += child.subtree_hash
        return hashlib.sha1(hash_val).hexdigest()

    def __unicode__(self):
        #ancestry = self.get_ancestors(include_self=True)
        #unicode_val = unicode(ancestry[0].path)
        #if len(ancestry) > 1:
        #    unicode_val += unicode(":")
        #    unicode_val += u'\u2192'.join(
        #        [unicode(n.path) for n in ancestry[1:]])
        #return unicode_val
        return self.subtree_hash

    ## def get_shot(self):
    ##     if self.level==0:
    ##         shot = int(self.path)
    ##     else:
    ##         root_node = self.get_root()
    ##         shot = int(root_node.path)
    ##     return shot

    def populate_child_nodes(self):
        """Use primary data source to populate child nodes."""

        child_names = self.get_child_names_from_primary_source()
        for child in child_names:
            node = SubTree(path=child, parent=self, shot=self.shot)
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

    def preprocess_filter_kwargs(self, kwargs):
        # TODO: should filters.http_arg be put here instead?
        for key, val in kwargs.iteritems():
            if isinstance(val, str) and "__shot__" in val:
                shot_str = str(self.shot.number)
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
        return unicode("%s: %s" % (self.time, self.signal))

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
        return unicode("[%s] %s" % (self.user, self.name))

    def get_absolute_url(self):
        return reverse("h1ds-user-worksheet", kwargs={
            "username": self.user.username,
            "worksheet": self.slug})


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
    url = models.URLField(max_length=2048, help_text=("URL of the signal. "
                                                      "If you want the signal to show the currently viewed shot, "
                                                      "then replace the shot number with {{shot}}. "
                                                      "The URL is parsed as a Django template, so standard template "
                                                      "filters can be used, such as {{shot|add:'-1'}} or"
                                                      "{{shot|add:'1'}} to show the previous and next shots, "
                                                      "respectively."))
    name = models.CharField(max_length=1024)
    ordering = models.IntegerField(blank=True)

    def __unicode__(self):
        return unicode("%s" % self.name)


class UserSignalForm(ModelForm):
    class Meta:
        model = UserSignal
        fields = ('name', )


class UserSignalUpdateForm(ModelForm):
    class Meta:
        model = UserSignal

