from celery import task, chord
from django.db import transaction

from h1ds_summary import TABLE_NAME_TEMPLATE
from h1ds_summary import get_summary_cursor

from celery.signals import task_sent



def shot_exists(cursor, table_name, shot_number):
    cursor.execute('SELECT shot from {} WHERE shot={}'.format(table_name, shot_number))
    return bool(cursor.fetchone())

@task()
def get_summary_attribute_data(device_slug, shot_number, attribute_slug):
    """Get data for summary attribute for a given shot.

    Arguments:
        device_slug (str) - slug for a h1ds.models.Device instance
        shot_number (int) - shot number to get data for.
        attribute_slug (str) - slug for an instance of h1ds.models.SummaryAttribute which belongs to the device.

    Returns:
        (attr_slug, data)

    """
    # TODO: Can the imports be rearranged so we don't have to import here?
    from h1ds_summary.models import SummaryAttribute

    attribute = SummaryAttribute.objects.get(slug=attribute_slug, device__slug=device_slug)
    try:
        data = attribute.get_value(shot_number)
    except:  # TODO: be more sensible about exception handling
        data = None
    return attribute_slug, data


@task()
def insert_table_attributes(attribute_data, **kwargs):
    """Write attributes to summary database.

    Keyword arguments:
       table_name (str) - name of SQLite table to write to
       shot_number (int) - shot number
       shot_timestamp
    Arguments
       *args - remaining args should be (attr, data) pairs

    e.g. write_attributes_to_table('my_table', 12345, ('dens',10), ('Ti',9))

    """
    # We use **kwargs because celery chaining pushes previous results to the
    # first argument of successive tasks, and kwargs let us set up a partial
    # where not arguments are not interchangeable (here, table_name and shot_number)
    table_name = kwargs.get('table_name')
    shot_number = kwargs.get('shot_number')
    shot_timestamp = kwargs.get('shot_timestamp')


    cursor = get_summary_cursor()
    attr_str = 'shot,timestamp'
    value_str = "{},'{}'".format(shot_number, shot_timestamp)
    for attr in attribute_data:
        attr_str += ',{}'.format(attr[0])
        if attr[1] is None:
            value_str += ',NULL'
        else:
            value_str += ',{}'.format(attr[1])

    cursor.execute('INSERT OR REPLACE INTO {} ({}) VALUES ({})'.format(table_name, attr_str, value_str))
    transaction.commit_unless_managed(using='summarydb')  # TODO: can drop w/ Django 1.6

@task()
def update_table_attributes(attribute_data, **kwargs):
    """Write attributes to summary database.

    Keyword arguments:
       table_name (str) - name of SQLite table to write to
       shot_number (int) - shot number
       shot_timestamp
    Arguments
       *args - remaining args should be (attr, data) pairs  (TODO: BUG: currently all implementations provide args=(((a, d), (a, d)),) )

    e.g. write_attributes_to_table('my_table', 12345, ('dens',10), ('Ti',9))

    """
    # We use **kwargs because celery chaining pushes previous results to the
    # first argument of successive tasks, and kwargs let us set up a partial
    # where not arguments are not interchangeable (here, table_name and shot_number)
    table_name = kwargs.get("table_name")
    shot_number = kwargs.get("shot_number")
    shot_timestamp = kwargs.get("shot_timestamp")

    cursor = get_summary_cursor()
    attribute_data += (("timestamp", "'{}'".format(shot_timestamp)), )

    set_str = ",".join("{}=NULL".format(a[0]) if (a[1] is None) else "{}={}".format(a[0], a[1]) for a in attribute_data)

    cursor.execute("UPDATE {} SET {} WHERE shot={}".format(table_name, set_str, shot_number))
    transaction.commit_unless_managed(using='summarydb')  # TODO: can drop w/ Django 1.6



@task()
def insert_single_table_attribute(device_slug, shot_number, shot_timestamp, attribute_slug):
    """Get a data for a single summary attribute and write it to the table.

    Arguments:
        device slug (str) - slug for device
        shot_number (int) - shot number
        attribute_slug (str) - slug for SummaryAttribute for device.

    """
    table_name = TABLE_NAME_TEMPLATE.format(device_slug)
    chord([get_summary_attribute_data.s(device_slug, shot_number, attribute_slug)],
          insert_table_attributes.s(table_name=table_name, shot_number=shot_number, shot_timestamp=shot_timestamp)).apply_async()

@task()
def update_single_table_attribute(device_slug, shot_number, shot_timestamp, attribute_slug):
    """Get a data for a single summary attribute and write it to the table.

    Arguments:
        device slug (str) - slug for device
        shot_number (int) - shot number
        attribute_slug (str) - slug for SummaryAttribute for device.

    """
    table_name = TABLE_NAME_TEMPLATE.format(device_slug)
    chord([get_summary_attribute_data.s(device_slug, shot_number, attribute_slug)],
          update_table_attributes.s(table_name=table_name, shot_number=shot_number,shot_timestamp=shot_timestamp)).apply_async()

@task
def insert_or_update_single_table_attribute(device_slug, shot_number, shot_timestamp, attribute_slug):
    cursor = get_summary_cursor()
    table_name = TABLE_NAME_TEMPLATE.format(device_slug)
    if shot_exists(cursor, table_name, shot_number):
        update_single_table_attribute(device_slug, shot_number, shot_timestamp, attribute_slug)
    else:
        insert_single_table_attribute(device_slug, shot_number, shot_timestamp, attribute_slug)

@task_sent.connect  #(sender='h1ds.tasks.populate_tree_success')
def test_signal(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    if sender == 'h1ds.tasks.populate_tree_success':  #TODO should be able to put this in connect - but not working?
        from h1ds.models import Device
        from h1ds_summary.db import SummaryTable
        device_slug, shot_number, tree = args[0]
        # TODO: should this be a celery task?
        device = Device(slug=device_slug)
        db = SummaryTable(device)
        db.update_shot(shot_number)
