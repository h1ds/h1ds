"""Module for communicating with MDSplus backend."""

import MDSplus
from MDSplus import TdiException
from MDSplus._treeshr import TreeNoDataException

from h1ds_core.base import BaseNodeData

class NodeData(BaseNodeData):

    def _get_mds_node_info(self):
        """Get MDS path for node.

        Node ancestry is [shot, tree, node0, node1, ...].
        """
        node_ancestors = list(self.get_ancestors(include_self=True))
        mds_shot = self.shot
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
            mds_tree = MDSplus.Tree(tree, shot)
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

    
