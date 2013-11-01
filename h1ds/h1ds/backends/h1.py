"""H1 backend."""

from datetime import datetime
import MDSplus
from h1ds.backends import mdsplus

class DataInterface(mdsplus.DataInterface):
    pass


class TreeLoader(mdsplus.TreeLoader):
    pass


class H1ShotManager(mdsplus.MDSPlusShotManager):
    def get_timestamp_for_shot(self, shot):
        from h1ds.models import Tree

        try_these = (
            "\\h1data::top.operations:h18212sl:input_07",
            "\\h1data::top.operations:h18212sl:input_01",
        )
        h1ds_tree = Tree.objects.get(slug='h1data')
        h1ds_tree.load()
        tree = MDSplus.Tree(str(h1ds_tree.slug), shot)
        min_time = datetime(1970, 1, 1, 0, 0)
        time_inserted = min_time
        for node in try_these:
            n = tree.getNode(node)
            mds_time = n.getTimeInserted()
            # convert MDSplus time into a Python dattime object
            time_inserted = datetime.strptime(str(mds_time._getDate()), "%d-%b-%Y %H:%M:%S.%f")
            if time_inserted > min_time:
                break
        return time_inserted
