from celery import task


@task()
def populate_tree(shot):
    """Asynchronously populate a data tree."""
    # Import here to avoid circular imports.
    from h1ds.models import Node

    for tree in Node.datatree.get_trees():
        node = Node(path=tree, shot=shot)
        node.save()
        node.populate_child_nodes()
