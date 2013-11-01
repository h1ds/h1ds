"""Module for communicating with MDSplus backend."""

import os
import numpy as np
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

import MDSplus
from MDSplus import TdiException
from MDSplus._treeshr import TreeNoDataException, TreeException

# TODO: base vs models - it's not intuitive what should be where...
from h1ds.base import BaseDataInterface
from h1ds.base import BaseBackendShotManager, BaseTreeLoader


class TreeLoader(BaseTreeLoader):

    def load(self, tree):
        os.environ[tree.name + "_path"] = tree.configuration


class DataInterface(BaseDataInterface):

    def _get_mds_node_info(self):
        """Get MDS path for node.

        """
        mds_path = ".".join([str(p) for p in self.path])
        return self.shot, str(self.tree.name), mds_path

    def _get_mds_node(self):
        """Get the corresponding MDSplus node for this H1DS tree node."""

        if not hasattr(self, '_mds_node'):
            shot, tree, path = self._get_mds_node_info()
            try:
                mds_tree = MDSplus.Tree(tree, shot)
            except TreeException:
                # Tree doesn't exist for this shot.
                # Raise django exception, rather than backend specific
                # exception
                raise ObjectDoesNotExist
            if path == "":
                self._mds_node = mds_tree.getDefault()
            else:
                self._mds_node = mds_tree.getNode(path)
        return self._mds_node

    def get_name(self):
        node = self._get_mds_node()
        return str(node)

    def get_value(self):
        #if not self.parent:
        #    return None
        mds_node = self._get_mds_node()
        try:
            primary_data = mds_node.getData().data()
        except (TreeNoDataException, TdiException, AttributeError):
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
        mds_node = self._get_mds_node()
        try:
            shape = mds_node.getShape()
            if len(shape) == 1:
                raw_dim = [mds_node.getDimensionAt().data()]
            else:
                dim_list = []
                for i in range(len(shape)):
                    dim_list.append(mds_node.getDimensionAt(i).data())
                raw_dim = np.array(dim_list)
        except TdiException:
            raw_dim = []  # np.array([])
        return raw_dim

    def get_value_units(self):
        node = self._get_mds_node()
        try:
            units = node.getData().getUnits()
        except:
            units = ""
        return units

    def get_dimension_units(self):
        #if not self.parent:
        #    return np.array([])
        mds_node = self._get_mds_node()
        try:
            shape = mds_node.getShape()
            if len(shape) == 1:
                dim_units = mds_node.getDimensionAt().getUnits()
            else:
                units_list = []
                for i in range(len(shape)):
                    units_list.append(mds_node.getDimensionAt(i).getUnits())
                dim_units = units_list
        except TdiException:
            dim_units = ""
        return dim_units

    def get_value_dtype(self):
        value = self.get_value()
        try:
            dtype = str(value.dtype)
        except:
            dtype = ""
        return dtype

    def get_dimension_dtype(self):
        dim = self.get_dimension()
        try:
            dtype = str(dim.dtype)
        except:
            dtype = ""
        return dtype

    def get_metadata(self):
        return {}

    def get_children(self):
        try:
            mds_node = self._get_mds_node()
        except ObjectDoesNotExist:
            return []
        mds_descendants = mds_node.getDescendants()
        if type(mds_descendants) == type(None):
            node_names = []
        else:
            node_names = [n.getNodeName() for n in mds_descendants]
        children = []
        for child_name in node_names:
            children.append(DataInterface(shot=self.shot, tree=self.tree, path=self.path + [child_name]))
        return children


class MDSPlusShotManager(BaseBackendShotManager):
    pass
