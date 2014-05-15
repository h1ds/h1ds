"""Generic HDF5 backend for H1DS."""

import os
import tables
import numpy as np
from h1ds.base import BaseBackendShotManager
from h1ds.base import BaseDataInterface
from h1ds.base import BaseTreeLoader

def shot_group(shot_number):
    return "shot_{}".format(shot_number)

class Signal1D(tables.IsDescription):
    """This is intended for testing, more generic datatypes are
    needed.

    """
    name=tables.StringCol(32)
    value=tables.UInt16Col() # col type should be set dynamically for given dtype
    dimension=tables.UInt16Col() # col type should be set dynamically for given dtype

    


# TODO: refactor - put this in DataInterface
def save_tree(tree):
    f = tables.open_file(tree.configuration, mode='a', title=tree.name)
    for shot_range in tree.shot_ranges.all():
        for shot_number in xrange(shot_range.min_shot, shot_range.max_shot+1):
            if not shot_group(shot_number) in f.root:
                f.create_group("/", shot_group(shot_number), 'Shot {}'.format(shot_number))
    f.close()
        

# TODO: refactor - put this in DataInterface
def save_node(node):
    """Write a H1DS node to its HDF5 file.

    TODO: refactor this as a DataInstance method.

    """
    tree = node.get_tree()
    f = tables.open_file(tree.configuration, mode='a', title=tree.name)
    base_group_path = '/'+shot_group(node.shot.number)
    node_group_path = '/'.join([base_group_path, '/'.join(node.node_path.get_path_components()[:-1])]).rstrip('/')
    node_name = node.node_path.get_path_components()[-1]
    node_group = f.create_group(node_group_path, node_name, createparents=True)
    f.create_array(node_group, 'value', np.array(node.data['value']), 'data value')
    f.create_array(node_group, 'dimension', np.array(node.data['dimension']), 'data dimension')
    f.close()

class Hdf5ShotManager(BaseBackendShotManager):
    pass

class DataInterface(BaseDataInterface):

    def _get_hdf5_file(self):
        return tables.open_file(self.tree.configuration, mode='r', title=self.tree.name)
    
    def get_children(self):
        f = self._get_hdf5_file()
        result = f.list_nodes("/"+shot_group(self.shot), *self.path)
        f.close()
        return result

class TreeLoader(BaseTreeLoader):
    pass
