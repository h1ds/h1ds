"""
Module for communicating with MDSplus backend.
"""

import os

import numpy as np
#from django.conf import settings
#from django.core.exceptions import ObjectDoesNotExist

from django.conf import settings

from h1ds.lib.idam.exceptions import TreeNoDataException, TreeException
from h1ds.lib.idam import xpadsource

# TODO: base vs models - it's not intuitive what should be where...
from h1ds.base import BaseDataInterface
from h1ds.base import BaseTreeLoader

#from IDAM_base import BaseDataInterface
#from IDAM_base import BaseTreeLoader
from django.core.cache import cache


# TODO: this should be in treeloader (see hdf5.py)
def save_tree(tree):
    pass


class TreeLoader(BaseTreeLoader):

    def load(self, tree):
        # TODO: load tree file into cache
        pass



class DataInterface(BaseDataInterface):
    # According a chat with Dave: i shall not touch the methods _get_...
    def _get_idam_node_info(self):
        """Get IDAM path for node.

        """
        idam_path = ".".join([str(p) for p in self.path])
        return self.shot, str(self.tree.label), idam_path

    def _get_idam_node(self):
        """Get the corresponding IDAM node for this H1DS tree node."""

        if not hasattr(self, '_idam_node'):
            #shot, tree, path = self._get_idam_node_info()
            #print tree
            if settings.DEBUG:
                cache_name = '-debug-idam-{}-{}'.format(self.shot,self.tree.configuration)
            else:
                cache_name = '-idam-{}-{}'.format(self.shot,self.tree.configuration)
            print('cache name')
            print(cache_name)
            _idam_node = cache.get(cache_name)
            if _idam_node is None:
                try:
                    _idam_node = xpadsource.XPadSource(self.tree.configuration)
                    print('IDAM SOURCE')
                    print(_idam_node)
                    cache.set(cache_name, _idam_node)
                except TreeException:
                    # Tree doesn't exist for this shot.
                    # Raise django exception, rather than backend specific
                    # exception
                    raise ObjectDoesNotExist
            print('PATH')
            print(self.path)
            for path_element in self.path:
                found = False
                try:
                    children = _idam_node.children
                except AttributeError:
                    children = []

                for child in children:
                    if child.label.lower() == path_element.lower():
                        _idam_node = child
                        found = True
                        break
                #for var_name in _idam_node.varNames:
                #    if var_name.lower() == path_element.lower():
                        
                #if not found:
                #    raise Exception()
            self._idam_node = _idam_node
            self._value = None
        return self._idam_node

    def read_data(self,idam_node, path, shot):
        # cache reponses
        cache_name = '-idam-read-{}-{}-{}'.format(self.shot,self.tree.configuration, path)
        response = cache.get(cache_name)
        if response is None:
            response = idam_node.read(path, shot)
            cache.set(cache_name, response)
        return response

    def get_name(self):
        node = self._get_idam_node()
        name = node.label
        return str(name)

    def get_value(self):
        #if not self.parent:
        #    return None
	## return: return array or scalar 
        print('path', self.path)
        if self._value is not None:
            return self._value
        idam_node = self._get_idam_node()
        if len(self.path) == 0:
            self._value = []
            return self._value
        path_name = self.path[-1].replace('---', '/')
        print('path name')
        print(path_name)
        var_names = idam_node.varNames
        upper_varnames = list(map(str.upper, var_names))
        index = 0
        try:
            index = upper_varnames.index(path_name.upper())
        except ValueError:
            self._value = []
            return self._value
        #self._value = [idam_node.read(var_names[index], str(self.shot)).data]
        self._value = [self.read_data(idam_node, var_names[index], str(self.shot)).data]
        return self._value

        #####
        if path_name in idam_node.varNames:
            print('name found')
            self._value = [self.read_data(idam_node, path_name, str(self.shot)).data]
            return self._value
        else:
            self._value = []
            return self._value
        try:
            #primary_data = mds_node.getData().data()
            # quantity, shot_no: both are strings. 
            # e.g.: quantity="amc_plasma current", shot_no="15233"
            # get data and time
            dt = []
            try:
                dt.append(idam_node.data.time)
            except:
                pass
            # end   try:
            try:
                dt.append(idam_node.data.data)
            except:
                pass
            # end   try:
            if(dt):
                primary_data = np.array(dt)
            else:
                primary_data = None
            # end   if(dt):
        # Question: What to do with TdiException?
        #except (TreeNoDataException, TdiException, AttributeError):
        except (TreeNoDataException, AttributeError):
            print('except attribute error')
            primary_data = None
        if primary_data is None:
            return []
        if np.isscalar(primary_data):
            return [primary_data]
        elif len(primary_data.shape) == 1:
            return np.array([primary_data])
        else:
            return primary_data

    def get_dimension(self):
        """Get dimension of raw data (i.e. no filters)."""
        idam_node = self._get_idam_node()
        if len(self.path) == 0:
            return []
        path_name = self.path[-1].replace('---', '/')
        var_names = idam_node.varNames
        upper_varnames = list(map(str.upper, var_names))
        index = 0
        try:
            index = upper_varnames.index(path_name.upper())
        except ValueError:
            return []
        return [self.read_data(idam_node, var_names[index], str(self.shot)).time]


        if path_name in idam_node.varNames:
            return [self.read_data(idam_node, path_name, str(self.shot)).time]
        else:
            return []
        try:
            val = self.get_value()
            print('VALUE...')
            print(type(val))
            print(val)
            shape = val.shape
            print(shape)
            if len(shape) == 1:
                raw_dim = [np.arange(len(val))]
            else:
                dim_list = []
                #for i in range(len(shape)):
                #    dim_list.append(np.arange(len(val[i])))
                raw_dim = np.array(dim_list)
        # Question: What to do with TdiException?
        #except TdiException:
        except TreeNoDataException:
            raw_dim = []  # np.array([])
        except AttributeError:
            raw_dim = []
        return raw_dim

    def get_value_units(self):
        ## return: string
        idam_node = self._get_idam_node()
        try:
            units = idam_node.units
        except:
            units = ""
        return units

    def get_dimension_units(self):
        #if not self.parent:
        #    return np.array([])
	## return: string
        # Question: Are these units for x and y axes? Order [x,y] or [y,x]?
        idam_node = self._get_idam_node()
        try:
            val = self.get_value()
            shape = val.shape
            if len(shape) == 1:
                dim_units = idam_node.units
            else:
                units_list = []
                for i in range(len(idam_node.dim)):
                    units_list.append(idam_node.dim[i].units)
                units_list.append(idam_node.dim)
                units_list.append(idam_node.units)
                dim_units = units_list
        # Question: What to do with TdiException?
        #except TdiException:
        except (TreeNoDataException, AttributeError):
            dim_units = ""
        return dim_units

    def get_value_dtype(self):
        ## return: string
        value = self.get_value()
        try:
            dtype = str(value.dtype)
        except:
            dtype = ""
        return dtype

    def get_dimension_dtype(self):
        ## return: string
        dim = self.get_dimension()
        try:
            dtype = str(dim.dtype)
        except:
            dtype = ""
        return dtype

    def get_metadata(self):
        return {}

    def get_children(self):
        # Question: how to deal with the stuff in the for loop?
        #           shot is fine. but tree and path?
        idam_node = self._get_idam_node()
        #except ObjectDoesNotExist:
        #    return []
        children = []

        try:
            idam_descendants = idam_node.children
            node_names = [n.label for n in idam_descendants]
            for child in idam_descendants:
                children.append(DataInterface(shot=self.shot, tree=self.tree, path=self.path + [child.label]))
                
        except AttributeError:
            #node_names = []
            for var_name in idam_node.varNames:
                slug_name = var_name.replace('/', '---')
                children.append(DataInterface(shot=self.shot, tree=self.tree, path=self.path + [slug_name]))


        # end   try:

        # children = []
        # for child_name in node_names:
        #     children.append(DataInterface(shot=self.shot, tree=self.tree, path=self.path + [child_name]))
        # for varName in idam_node.varNames:
        #     slug_name = varName.replace('/', '---')
        #     children.append(DataInterface(shot=self.shot, tree=self.tree, path=self.path + [slug_name]))
            
        return children


