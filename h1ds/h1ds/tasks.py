from celery import task

from django.utils.importlib import import_module
from django.conf import settings

backend_module = import_module(settings.H1DS_DATA_BACKEND)


@task()
def populate_tree(shot, tree):
    """Asynchronously populate a data tree."""
    empty_path = []
    node_data = backend_module.DataInterface(shot=shot.number, tree=tree, path=empty_path)
    node = node_data.get_node()
