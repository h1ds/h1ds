"""Generic HDF5 backend for H1DS."""

import os
import tables
from h1ds.base import BaseBackendShotManager
from h1ds.base import BaseDataInterface
from h1ds.base import BaseTreeLoader

def shot_group(shot_number):
    return "shot_{}".format(shot_number)

# TODO: refactor - put this in DataInterface
def save_tree(tree):
    f = tables.open_file(tree.configuration, mode='a', title=tree.name)
    for shot_range in tree.shot_ranges.all():
        for shot_number in xrange(shot_range.min_shot, shot_range.max_shot+1):
            if not shot_group(shot_number) in f.root:
                f.create_group("/", shot_group(shot_number), 'Shot {}'.format(shot_number))
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
