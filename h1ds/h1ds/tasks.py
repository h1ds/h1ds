from celery import task


@task()
def populate_tree(shot, tree):
    """Asynchronously populate a data tree."""
    empty_path = []
    backend_module = tree.get_backend_module()
    node_data = backend_module.DataInterface(shot=shot.number, tree=tree, path=empty_path)
    node = node_data.get_node()
    return shot.device.slug, shot.number, tree.slug

@task()
def populate_tree_success(*args, **kwargs):
    """Dummy task which is used as a callback for populate_tree so we can use celery signals task_sent.

    we could listen to task_success from populate_tree, but we can't filter for sender and we don't want
    to listen to all tasks.

    """
    return None