"""Base classes for interaction with database.

"""
import inspect
import datetime
import hashlib
import re
import numpy as np
from django.db import models
from django.conf import settings
from django.utils.importlib import import_module
from h1ds.filters import BaseFilter, excluded_filters


# Match strings "f(fid)_name", where fid is the filter ID
filter_name_regex = re.compile('^f(?P<fid>\d+?)')

# Match strings "f(fid)_kwarg_(arg name)", where fid is the filter ID
filter_kwarg_regex = re.compile('^f(?P<fid>\d+?)_(?P<kwarg>.+)')

sql_type_mapping = {
    np.float32: "FLOAT",
    np.float64: "FLOAT",
    np.int32: "INT",
    np.int64: "INT",
}


def remove_prefix(url):
    """Strip any prefix in the URL path."""
    if url.startswith("/"):
        url = url[1:]
    if hasattr(settings, "H1DS_DATA_PREFIX"):
        pref = settings.H1DS_DATA_PREFIX + "/"
        if url.startswith(pref):
            url = url[len(pref):]
    return url


def apply_prefix(url):
    """Apply any prefix to the URL path."""
    if not url.startswith("/"):
        url = "/" + url
    if hasattr(settings, "H1DS_DATA_PREFIX"):
        if not url.startswith("/" + settings.H1DS_DATA_PREFIX + "/"):
            url = "/" + settings.H1DS_DATA_PREFIX + url
    return url


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


class Data(object):
    def __init__(self, name="", value=None, dimension=None, value_units="", dimension_units="", value_dtype="",
                 dimension_dtype="", metadata=None, value_labels=None, dimension_labels=None):
        if not dimension_labels: dimension_labels = []
        if not value_labels: value_labels = []
        if not metadata: metadata = {}
        self.name = name
        self.value = value
        self.dimension = dimension
        self.value_units = value_units
        self.dimension_units = dimension_units
        self.value_dtype = value_dtype
        self.dimension_dtype = dimension_dtype
        self.value_labels = value_labels
        self.dimension_labels = dimension_labels
        if hasattr(value, "len") and len(self.value) > len(self.value_labels):
            self.value_labels = ["channel_%d" % (i + 1) for i in range(self.get_n_channels())]
        if hasattr(dimension, "len") and len(self.dimension) > len(self.dimension_labels):
            self.dimension_labels = ["dimension_%d" % (i + 1) for i in range(self.get_n_dimensions())]
        self.metadata = metadata

    def get_n_dimensions(self):
        return len(self.dimension)

    def get_n_channels(self):
        return len(self.value)

    def get_signal_length(self):
        if np.isscalar(self.value[0]):
            return 0
        else:
            return len(self.value[0])


def has_data(value):
    result = False
    if hasattr(value, "__iter__"):
        for v in value:
            if v is not None:
                result = True
                break
    else:
        if value is not None:
            result = True
    return result


class BaseDataInterface(object):
    """Base interface class for backend data sources.

    This class essentially sets out the API, with the subclass expected to overwrite most methods.

    """
    def __init__(self, shot, tree, path):
        """
        Args:
            shot (int) - shot number
            tree (h1ds.models.Tree) - tree instance
            path (list) - list of path components
        """
        self.shot = shot
        self.tree = tree
        self.path = [p.lower() for p in path]

        self.tree.load()

    def generate_hash(self, has_data=False, n_dimensions=0, dtype="", n_channels=0, child_nodes=[]):
        hash_val = ""
        for field in [has_data, n_dimensions, dtype, n_channels]:
            hash_val += hashlib.sha1(unicode(field)).hexdigest()
        for child in sorted(child_nodes, key=lambda x: x.subtree.subtree_hash):
            hash_val += child.subtree.subtree_hash
        return hashlib.sha1(hash_val).hexdigest()

    def get_node(self, fallback=False):
        """If Node instance exits, return it, otherwise generate node and subtree"""
        from h1ds.models import SubTree, NodePath, Shot, Node

        if fallback:
            node = Node.fallback.create_node(shot_number=self.shot, tree=self.tree, nodepath='/'.join(self.path))
            return node

        child_nodes = self.get_child_nodes()
        data = self.read_primary_data()
        node_has_data = has_data(data.value)
        n_dimensions = data.get_n_dimensions()
        dtype = data.value_dtype
        n_channels = data.get_n_channels()
        hash = self.generate_hash(has_data=node_has_data, n_dimensions=n_dimensions, dtype=dtype, n_channels=n_channels, child_nodes=child_nodes)
        try:
            subtree = SubTree.objects.get(subtree_hash=hash)
        except SubTree.DoesNotExist:
            subtree = SubTree(has_data=node_has_data, n_dimensions=n_dimensions, dtype=dtype, n_channels=n_channels, subtree_hash=hash)
            subtree.save()
            subtree.children.add(*(c.subtree for c in child_nodes))

        shot, shot_created = Shot.objects.get_or_create(number=self.shot)  # TODO: need device here.

        parent_nodepath = self.get_parent_nodepath(self.path, self.tree)
        fullpath = self.get_fullpath()
        nodepath, nodepath_created = NodePath.objects.get_or_create(path=fullpath, tree=self.tree, defaults={'parent': parent_nodepath})

        node = Node(node_path=nodepath, shot=shot, subtree=subtree)
        node.save()

        return node

    def get_fullpath(self):
        return "/".join([str(p) for p in self.path])

    def get_parent_nodepath(self, path, tree):
        from h1ds.models import NodePath
        if len(path) == 0:
            return None
        elif len(path) == 1:
            # TODO: creating the top node should be done somwehere more visible - probably during Tree.load()
            nodepath, created = NodePath.objects.get_or_create(path=NodePath.TOP_PATH, tree=tree, defaults={'parent': None})
            return nodepath
        else:
            grandparent_nodepath = self.get_parent_nodepath(path=path[:-1], tree=tree)
            fullpath = "/".join([str(p) for p in path[:-1]])
            nodepath, nodepath_created = NodePath.objects.get_or_create(path=fullpath, tree=tree, defaults={'parent':grandparent_nodepath})
            return nodepath

    def get_child_nodes(self, fallback=False):
        return [child.get_node(fallback=fallback) for child in self.get_children()]

    def get_children(self):
        """Return Datainterface instances for each child"""
        pass

    def get_name(self):
        return ""

    def get_value(self):
        return None

    def get_dimension(self):
        return None

    def get_value_units(self):
        return ""

    def get_dimension_units(self):
        return ""

    def get_value_dtype(self):
        return ""

    def get_dimension_dtype(self):
        return ""

    def get_metadata(self):
        return {}

    def read_primary_data(self):
        name = self.get_name()
        value = self.get_value()
        dimension = self.get_dimension()
        value_units = self.get_value_units()
        dimension_units = self.get_dimension_units()
        value_dtype = self.get_value_dtype()
        dimension_dtype = self.get_dimension_dtype()
        metadata = self.get_metadata()
        data = Data(name=name, value=value, dimension=dimension, value_units=value_units,
                    dimension_units=dimension_units, value_dtype=value_dtype,
                    dimension_dtype=dimension_dtype, metadata=metadata)

        return data

    def write_primary_data(self):
        pass


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
            if not filter_dict.has_key(fid):
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


class BaseBackendShotManager(models.Manager):
    """Base class for interactiing with backend shots."""

    def get_latest_shot(self):
        pass

    def get_timestamp_for_shot(self, shot):
        return datetime.datetime.now()

    def get_min_shot_number(self):
        return self.model.objects.all().aggregate(models.Min('number'))['number__min']

    def get_max_shot_number(self):
        return self.model.objects.all().aggregate(models.Max('number'))['number__max']

    def get_next_shot_number(self, shot_number):
        """Get value of next shot.

        Usually, this will be shot_number+1...

        """
        next_shot = self.model.objects.filter(number__gt=shot_number).aggregate(models.Min('number'))['number__min']
        return next_shot

    def get_previous_shot_number(self, shot_number):
        """Get value of previous shot.

        Usually, this will be shot_number-1...

        """
        previous_shot = self.model.objects.filter(number__lt=shot_number).aggregate(models.Max('number'))['number__max']
        return previous_shot


class BaseTreeLoader(object):
    """Load any settings for Tree object, e.g. env variables."""


    def load(self, tree):
        """override in backend."""
        pass