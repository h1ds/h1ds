"""Module for communicating with MDSplus backend."""

import os
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

import MDSplus
from MDSplus import TdiException
from MDSplus._treeshr import TreeNoDataException, TreeException

# TODO: base vs models - it's not intuitive what should be where...
from h1ds_core.base import BaseNodeData
from h1ds_core.base import BaseDataTreeManager
# Load MDS trees into environment
for config_tree in settings.EXTRA_MDS_TREES:
    os.environ[config_tree[0]+"_path"] = config_tree[1]


class NodeData(BaseNodeData):

    def _get_mds_node_info(self):
        """Get MDS path for node.

        Node ancestry is [shot, tree, node0, node1, ...].
        """
        node_ancestors = list(self.get_ancestors(include_self=True))
        mds_shot = int(node_ancestors[0].path)
        # force str rather than unicode. unicode hits mds bug?
        # not tested since refactor, so casting to str may not be required.
        mds_tree = str(node_ancestors[1].path)
        mds_path = ""
        if len(node_ancestors) > 2:
            mds_path = ".".join([n.path for n in node_ancestors[2:]])
        return mds_shot, mds_tree, mds_path
    
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

    def read_raw_data(self):
        mds_node = self._get_mds_node()
        try:
            raw_data = mds_node.getData().data()
        except (TreeNoDataException, TdiException, AttributeError):
            raw_data = None
        return raw_data

    def get_child_names_from_primary_source(self):
        try:
            mds_node = self._get_mds_node()
        except ObjectDoesNotExist:
            return []
        mds_descendants = mds_node.getDescendants()
        if type(mds_descendants) == type(None):
            node_names = []
        else:
            node_names = [n.getNodeName() for n in mds_descendants]
        return node_names
        
        
    
class DataTreeManager(BaseDataTreeManager):
    def get_trees(self):
        # TODO: no longer support  getting trees from environment, use
        # explicit definitions in settings file.
        # TODO: rename EXTRA_MDS_TREES to something like MDSPLUS_TREES
        tree_names = [i[0] for i in settings.EXTRA_MDS_TREES]
        return tree_names

    def populate_shot(self, shot_root_node):
        for tree_name in self.get_trees():
            node = self.model(path=tree_name, parent=shot_root_node)
            node.save()
            node.populate_child_nodes()
