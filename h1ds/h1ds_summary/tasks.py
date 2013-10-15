from celery import task, chain
from django.db import transaction

from h1ds.utils import get_backend_shot_manager
from h1ds_summary import TABLE_NAME_TEMPLATE
from h1ds_summary import get_summary_cursor

backend_shot_manager = get_backend_shot_manager()


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
def write_attributes_to_table(*args, **kwargs):
    """Write attributes to summary database.

    Keyword arguments:
       table_name (str) - name of SQLite table to write to
       shot_number (int) - shot number
    Arguments
       *args - remaining args should be (attr, data) pairs

    e.g. write_attributes_to_table('my_table', 12345, ('dens',10), ('Ti',9))

    """
    # We use **kwargs because celery chaining pushes previous results to the
    # first argument of successive tasks, and kwargs let us set up a partial
    # where not arguments are not interchangeable (here, table_name and shot_number)
    table_name = kwargs.get("table_name")
    shot_number = kwargs.get("shot_number")

    attr_str = "shot"
    value_str = str(shot_number)
    for attr in args:
        attr_str += ",{}".format(attr[0])
        if attr[1] is None:
            value_str += ",NULL"
        else:
            value_str += ",{}".format(attr[1])

    cursor = get_summary_cursor()
    cursor.execute("INSERT OR REPLACE INTO {} ({}) VALUES ({})".format(table_name, attr_str, value_str))
    transaction.commit_unless_managed(using='summarydb')  # TODO: can drop w/ Django 1.6


@task()
def write_single_attribute_to_table(device_slug, shot_number, attribute_slug):
    """Get a data for a single summary attribute and write it to the table.

    Arguments:
        device slug (str) - slug for device
        shot_number (int) - shot number
        attribute_slug (str) - slug for SummaryAttribute for device.

    """
    table_name = TABLE_NAME_TEMPLATE.format(device_slug)
    chain(get_summary_attribute_data.s(device_slug, shot_number, attribute_slug),
          write_attributes_to_table.s(table_name=table_name, shot_number=shot_number)).apply_async()
