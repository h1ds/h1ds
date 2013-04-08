import re
import datetime
import numpy as np
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

import h1ds_core.filters

data_module = import_module(settings.H1DS_DATA_MODULE)

# Match strings "f(fid)_name", where fid is the filter ID
filter_name_regex = re.compile('^f(?P<fid>\d+?)_name')

# Match strings "f(fid)_arg(arg number)", where fid is the filter ID
filter_arg_regex = re.compile('^f(?P<fid>\d+?)_arg(?P<argn>\d+)')

# Match strings "f(fid)_kwarg_(arg name)", where fid is the filter ID
filter_kwarg_regex = re.compile('^f(?P<fid>\d+?)_kwarg_(?P<kwarg>.+)')

sql_type_mapping = {
    np.float32:"FLOAT",
    np.float64:"FLOAT",
    np.int32:"INT",
    np.int64:"INT",
    }

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

class BaseURLProcessor(object):
    def __init__(self, **kwargs):
        """takes url or components.

        maps to /tree/shot/path.
        Use a subclass of this to change mapping.

        """
        url = kwargs.get('url', None)
        tree = kwargs.get('tree', None)
        shot = kwargs.get('shot', None)
        path = kwargs.get('path', None)
        if url != None:
            url = self.remove_prefix(url)
            self.tree, self.shot, self.path = self.get_components_from_url(url)
            if tree != None and tree != self.tree:
                raise AttributeError
            if shot != None and shot != self.shot:
                raise AttributeError
            if path != None and path != self.path:
                raise AttributeError
        else:
            self.tree, self.shot, self.path = tree, shot, path

    def remove_prefix(self, url):
        if url.startswith("/"):
            url = url[1:]
        if hasattr(settings, "H1DS_DATA_PREFIX"):
            pref = settings.H1DS_DATA_PREFIX + "/"
            if url.startswith(pref):
                url = url[len(pref):]        
        return url

    def apply_prefix(self, url):
        if not url.startswith("/"):
            url = "/"+url
        if hasattr(settings, "H1DS_DATA_PREFIX"):
            if not url.startswith("/"+settings.H1DS_DATA_PREFIX+"/"):
                url = "/"+settings.H1DS_DATA_PREFIX+ url
        return url
    
    def get_components_from_url(self, url):
        stripped_url = url.strip("/")
        n_slash = stripped_url.count("/")
        if n_slash == 0:
            tree = self.deurlize_tree(stripped_url)
            shot = data_module.get_latest_shot(tree)
            path = self.deurlize_path("")
        elif n_slash == 1:
            t, s = stripped_url.split("/")            
            tree = self.deurlize_tree(t)
            shot = self.deurlize_shot(s)
            path = self.deurlize_path("")
        else:
            t, s, p = stripped_url.split("/", 2)            
            tree = self.deurlize_tree(t)
            shot = self.deurlize_shot(s)
            path = self.deurlize_path(p)
        return tree, shot, path
        
    def get_url(self):
        return self.apply_prefix("/".join([self.urlized_tree(),
                                           self.urlized_shot(),
                                           self.urlized_path()]))
        
    def urlized_tree(self):
        return self.tree

    def urlized_shot(self):
        return str(self.shot)

    def urlized_path(self):
        return self.path

    def deurlize_tree(self, url_tree):
        if url_tree == "":
            return settings.DEFAULT_TREE
        else:
            return url_tree

    def deurlize_shot(self, url_shot):
        return int(url_shot)

    def deurlize_path(self, url_path):
        return url_path

class BaseNode(object):
    def __init__(self, url_processor=None):
        self.url_processor = url_processor
        self.filter_history = []
        self.data = None
        self.dim = None
        # TODO: get_ methods for following
        self.label = ('data',)
        
    def apply_filters(self, request):
        for fid, name, args, kwargs in get_filter_list(request):
            self.apply_filter(fid, name, *args, **kwargs)
        
    def apply_filter(self, fid, name, *args, **kwargs):
        d = self.get_data()
        f_args, f_kwargs = self.preprocess_filter_args(args, kwargs)
        filter_function = getattr(h1ds_core.filters, name)
        filter_function(self, *f_args, **f_kwargs)
        self.filter_history.append((fid, filter_function, args))
        #self.summary_dtype = sql_type_mapping.get(type(self.data))
        #self.available_filters = get_dtype_mappings(self.data)['filters']
        #self.available_views = get_dtype_mappings(self.data)['views'].keys()

    def preprocess_filter_args(self, args, kwargs):
        for i,a in enumerate(args):
            if isinstance(a, str):
                if "__shot__" in a:
                    args[i] = a.replace("__shot__", str(self.url_processor.shot))
        for k,v in kwargs.iteritems():
            if isinstance(v, str):
                if "__shot__" in v:
                    kwargs[k] = v.replace("__shot__", str(self.url_processor.shot))
        return args, kwargs
        
    def get_data(self):
        if type(self.data) == type(None):
            self.data = self.get_raw_data()
        return self.data

    def get_raw_dim(self):
        return None
    
    def get_dim(self):
        # TODO - scalars etc will have dim None, shouldn't re-read from node for these cases...
        if type(self.dim) == type(None):
            self.dim = self.get_raw_dim()
        return self.dim
                    
    def get_raw_data(self):
        return None
    
    def get_parent(self):
        return None

    def get_children(self):
        return None

    def get_ancestors(self):
        ancestors = []
        p = self.get_parent()
        if p != None:
            ancestors.extend(p.get_ancestors())
            ancestors.append(p)
        return ancestors
        
    def get_long_name(self):
        return unicode(self.url_processor.path)

    def get_short_name(self):
        return unicode(self.url_processor.path)

    def __str__(self):
        return self.get_long_name()

    def __repr__(self):
        return self.get_long_name()

    def get_data_time(self):
        return datetime.datetime.fromordinal(1)
    
    def get_summary_dtype(self):
        d = self.get_data()
        print "data: ", type(d)
        print "lkjdsf ", sql_type_mapping.get(type(d), None)
        return sql_type_mapping.get(type(d), None)
        

"""
class BaseDataInterface(object):

    node_class = Node
    
    def __init__(self, url_processor):
        self.url_processor = url_processor

    def get_data(self):
        return np.arange(0)
        
    def get_node(self):
        node = node_class(data=self.get_data(), url_processor=self.url_processor)
        return node
"""

        
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
