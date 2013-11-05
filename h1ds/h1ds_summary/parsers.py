"""Parsers for the H1DS summary uri path components."""

# TODO: latest shot from URL API component is defined from device, rather than from table
# this should be well documented...

#from h1ds_summary.db import SummaryTable
import itertools
from h1ds.models import Shot

def get_ranges_from_shot_slug(device, shot_slug):
    """Parse the URL path component corresponding to the requested shots."""

    # Put the shot string into lower case so we can easily match 'last'
    shot_str = shot_slug.lower()

    #if 'last' in shot_str:
    #    # Only touch the database if we need to...
    #    #table = SummaryTable(device)
    #    #latest_shot = table.get_latest_shot()
    #    #if latest_shot is None:
    #    #    return None

    # We'll put  shot ranges (e.g. "35790-35800" )  and individual shots
    # into separate lists as they  require different handling in the SQL
    # WHERE syntax.

    individual_shots = []
    shot_ranges = []

    # Now split the query into the separate components
    # i.e. "123+345-350" -> ["123", "345-350"]
    shot_components = shot_str.split('+')

    for shot_comp in shot_components:
        if shot_comp.startswith("last"):
            try:
                latest_shot = device.latest_shot.number
            except AttributeError:
                # device has no latest shot
                # TODO: fallback to maximum shot
                return None
            shot_ranges.append((device.latest_shot.number, device.latest_shot.number - int(shot_comp[4:])))
        elif '-' in shot_comp:
            shot_ranges.append(map(int, shot_comp.split('-')))
        else:
            individual_shots.append(shot_comp)
    return shot_ranges, individual_shots


def parse_shot_slug(device, shot_str):
    if shot_str.lower == 'all':
        return Shot.objects.filter(device=device).values_list('number', flat=True).order_by('-number')
    shot_ranges, individual_shots = get_ranges_from_shot_slug(device, shot_str)
    collected_shots = [range(i[0], i[1]+1) for i in shot_ranges]
    collected_shots.extend(individual_shots)
    # use set to remove duplicates
    return sorted(set(itertools.chain(*collected_shots)), reverse=True)



def get_where_from_shot_slug(device, shot_str):

    shot_ranges, individual_shots = get_ranges_from_shot_slug(device, shot_str)
    # Note that the SQL BETWEEN  operator requires the first argument to
    # be smaller than the second
    shot_where = " OR ".join("shot BETWEEN %d and %d" % (min(i), max(i)) for i in shot_ranges)

    if len(individual_shots) > 0:
        if shot_where != '':
            shot_where += " OR "
        shot_where += "shot IN (%s)" % (','.join(i for i in individual_shots))

    return shot_where


def parse_attr_str(device, attr_str):
    """Parse URL component corresponding to selected attributes.

    Arguments:
        device (h1ds.models.Device) - device instance for the summary table
        attr_str (str) - URL path component for attribute selection

    If attr_str is:
     * default: only SummaryAttributes with is_default = True are used.
     * all:     All SummaryAttributes are used
     * a+b+c+d: Attributes named 'a', 'b', 'c' and 'd' are used.

    Return a list of attribute slug names (not including 'shot').
    """
    from h1ds_summary.models import SummaryAttribute
    if 'all' in attr_str.lower():
        return list(SummaryAttribute.objects.filter(device=device).values_list('slug', flat=True))

    attr_slugs = []
    for attr_slug in attr_str.lower().split('+'):
        if attr_slug == 'default':
            attr_slugs.extend(list(
                SummaryAttribute.objects.filter(device=device, is_default=True).values_list('slug', flat=True)))
        else:
            attr_slugs.append(attr_slug)
    return attr_slugs


def parse_filter_str(filter_str):
    """Parse URL path component corresponding to SQL queries.

    SQL queries are separated by '+', and query components by '__' e.g.:
      mean_mirnov__gt__1.2+n_e__bw__0.5__1.5
    """
    if filter_str is None:
        return None
    filter_where_list = []
    filter_queries = filter_str.split("+")
    for filter_query_number, filter_query in enumerate(filter_queries):
        f = filter_query.split("__")
        if f[1].lower() == 'gt':
            filter_where_list.append("%s > %f" % (f[0], float(f[2])))
        elif f[1].lower() == 'lt':
            filter_where_list.append("%s < %f" % (f[0], float(f[2])))
        elif f[1].lower() == 'gte':
            filter_where_list.append("%s >= %f" % (f[0], float(f[2])))
        elif f[1].lower() == 'lte':
            filter_where_list.append("%s <= %f" % (f[0], float(f[2])))
        elif f[1].lower() in ['bw', 'between']:
            filter_where_list.append("%s BETWEEN %f AND %f" % (f[0], float(f[2]), float(f[3])))
    filter_where_string = " AND ".join(filter_where_list)
    return filter_where_string


def add_attr_to_path_component(active_attrs, attr_to_add):
    """Get a URL path component for added attribute

    Arguments:
        active_attrs (sequence) - list of slugs of active attributes
        attr_to_add (str) - slug of attribute to add.

    Returns:
        str - attr_str which can be used as URL component

    """
    new_attrs = list(active_attrs)
    if not attr_to_add in new_attrs:
        new_attrs.append(attr_to_add)
    return "+".join(new_attrs)


def remove_attr_from_path_component(active_attrs, attr_to_remove):
    """Get a URL path component for added attribute

    Arguments:
        active_attrs (sequence) - list of slugs of active attributes
        attr_to_remove (str) - slug of attribute to remove.

    Returns:
        str - attr_str which can be used as URL component

    """
    new_attrs = list(active_attrs)
    new_attrs.remove(attr_to_remove)
    if new_attrs:
        return "+".join(new_attrs)
    else:  # active_attrs is empty
        return "default"


def get_attribute_variants(device, all_attrs, attr_str):
    """Get variations on URL attribute_str from adding or removing attributes.

    Arguments:
        device (h1ds.models.Device) - device instance for the summary table
        all_attrs - iterable of all attribute slugs in the summary table.
        attr_str - attribute description string from the current url

    Returns:
        list of dicts of format {'slug':(str), 'attr_str':(str), 'is_active':(bool)} where attr_str is
        the attribute URL component for adding (if is_active is False) or removing (if is_active is True)
        the attribute

    """
    active_attrs = parse_attr_str(device, attr_str)
    inactive_attrs = [a for a in all_attrs if not a in active_attrs]

    output = []

    for attr in active_attrs:
        output.append({'slug': attr,
                       'attr_str': remove_attr_from_path_component(active_attrs, attr),
                       'is_active': True})
    for attr in inactive_attrs:
        output.append({'slug': attr,
                       'attr_str': add_attr_to_path_component(active_attrs, attr),
                       'is_active': False})

    return output
