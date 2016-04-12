"""
Module for communicating with MDSplus backend.
"""

import os

import numpy as np
#from django.conf import settings
#from django.core.exceptions import ObjectDoesNotExist

from h1ds.lib.idam.exceptions import TreeNoDataException, TreeException
from h1ds.lib.idam import xpadsource

# TODO: base vs models - it's not intuitive what should be where...
from h1ds.base import BaseDataInterface
from h1ds.base import BaseTreeLoader

#from IDAM_base import BaseDataInterface
#from IDAM_base import BaseTreeLoader


# TODO: this should be in treeloader (see hdf5.py)
def save_tree(tree):
    pass


class TreeLoader(BaseTreeLoader):

    def load(self, tree):
        os.environ[tree.name + "_path"] = tree.configuration



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
            shot, tree, path = self._get_idam_node_info()
            print tree
            try:
                tree = xpadsource.XPadSource(path)
            except TreeException:
                # Tree doesn't exist for this shot.
                # Raise django exception, rather than backend specific
                # exception
                raise ObjectDoesNotExist
            if path == "":
                self._idam_node = idam_tree.getDefault()
            else:
                dir(tree)
                self._idam_node = idam_tree.getNode(path)
        return self._idam_node

    def get_name(self):
        node = self._get_idam_node()
        name = node.label
        return str(name)

    def get_value(self):
        #if not self.parent:
        #    return None
	## return: return array or scalar 
        idam_node = self._get_idam_node()
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
            primary_data = None
        if np.isscalar(primary_data) or primary_data is None:
            return [primary_data]
        elif len(primary_data.shape) == 1:
            return np.array([primary_data])
        else:
            return primary_data

    def get_dimension(self):
        """Get dimension of raw data (i.e. no filters)."""
        #if not self.parent:  # top level
        #    return []  # np.array([])
	## return: numpy array
        idam_node = self._get_idam_node()
        try:
            val = self.get_value()
            shape = val.shape
            if len(shape) == 1:
                raw_dim = [mds_node.getDimensionAt().data()]
            else:
                dim_list = []
                for i in range(len(shape)):
                    dim_list.append(mds_node.getDimensionAt(i).data())
                raw_dim = np.array(dim_list)
        # Question: What to do with TdiException?
        #except TdiException:
        except TreeNoDataException:
            raw_dim = []  # np.array([])
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
        except TreeNoDataException:
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
        try:
            idam_node = self._get_idam_node()
        except ObjectDoesNotExist:
            return []
        try:
            idam_descendants = idam_node.children
            node_names = [n.label for n in idam_descendants]
        except:
            node_names = []
        # end   try:

        children = []
        for child_name in node_names:
            children.append(DataInterface(shot=self.shot, tree=self.tree, path=self.path + [child_name]))
        return children


