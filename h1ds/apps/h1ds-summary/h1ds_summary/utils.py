"""Various utility functions, kept here to keep models.py and views.py tidy."""
from datetime import datetime, MINYEAR
from colorsys import hsv_to_rgb

from django.db import connection, transaction
from django.db.utils import DatabaseError
from django.conf import settings
from django.core.cache import cache

import numpy

from h1ds_summary import SUMMARY_TABLE_NAME

CACHE_UPDATE_TIMEOUT = 60*60*24*365

SIGNAL_LENGTH = 2**16

try:
    canonical_shot = settings.H1DS_SUMMARY_CANONICAL_SHOT
except AttributeError:
    canonical_shot = 0

def drop_summary_table(table=SUMMARY_TABLE_NAME):
    cursor = connection.cursor()
    cursor.execute("DROP TABLE %s" %table)

def generate_base_summary_table(cursor, table = SUMMARY_TABLE_NAME):
    import h1ds_summary.models
    attrs = h1ds_summary.models.SummaryAttribute.objects.all()
    attr_string = ",".join(("%s %s" %(a.slug, a.get_value(0)[1]) for a in attrs))
    cols = ["shot MEDIUMINT UNSIGNED PRIMARY KEY",
            "timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP"]
    if attr_string != "":
        cols.append(attr_string)
    col_str = ','.join(cols)
    cursor.execute("CREATE TABLE %(table)s (%(cols)s)" %{'table':table, 'cols':col_str})
    cache.set('last_summarydb_update',datetime.now(), CACHE_UPDATE_TIMEOUT)

def get_latest_shot_from_summary_table(table = SUMMARY_TABLE_NAME):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT MAX(shot) FROM %(table)s" %{'table':table})
    except DatabaseError:
        generate_base_summary_table(cursor)
        cursor.execute("SELECT MAX(shot) FROM %(table)s" %{'table':table})

    latest_shot = cursor.fetchone()[0]
    return latest_shot

########################################################################
## URL path parsers for summary database                              ##
########################################################################

def parse_shot_str(shot_str, table=SUMMARY_TABLE_NAME):
    """Parse the URL path component corresponding to the requested shots."""

    # Put the shot string into lower case so we can easily match 'last'
    shot_str = shot_str.lower()

    if 'last' in shot_str:
        # Only touch the database if we need to...
        latest_shot = get_latest_shot_from_summary_table(table=table)
        if latest_shot == None:
            return None
        else:
            latest_shot = int(get_latest_shot_from_summary_table(table=table))

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
            shot_ranges.append((latest_shot, latest_shot-int(shot_comp[4:])))
        elif '-' in shot_comp:
            shot_ranges.append(map(int, shot_comp.split('-')))
        else:
            individual_shots.append(shot_comp)

    # Note that the SQL BETWEEN  operator requires the first argument to
    # be smaller than the second
    shot_where = " OR ".join("shot BETWEEN %d and %d" %(min(i), max(i)) for i in shot_ranges)

    if len(individual_shots) > 0:
        if shot_where != '':
            shot_where += " OR "
        shot_where += "shot IN (%s)" %(','.join(i for i in individual_shots))

    return shot_where

def parse_attr_str(attr_str):
    import h1ds_summary.models
    """Parse URL component corresponding to selected attributes.

    If attr_str is:
     * default: only SummaryAttributes with is_default = True are used.
     * all:     All SummaryAttributes are used
     * a+b+c+d: Attributes named 'a', 'b', 'c' and 'd' are used.

    Return a list of attribute slug names.
    """
    if 'all' in attr_str.lower():
        return list(h1ds_summary.models.SummaryAttribute.objects.values_list('slug', flat=True))

    attr_slugs = []
    for attr_slug in attr_str.lower().split('+'):
        if attr_slug == 'default':
            attr_slugs.extend(list(h1ds_summary.models.SummaryAttribute.objects.filter(is_default=True).values_list('slug', flat=True)))
        else:
            attr_slugs.append(attr_slug)
    return attr_slugs


def parse_filter_str(filter_str):
    """Parse URL path component corresponding to SQL queries.

    SQL queries are separated by '+', and query components by '__' e.g.:
      mean_mirnov__gt__1.2+n_e__bw__0.5__1.5
    """
    filter_where_list = []
    filter_queries = filter_str.split("+")
    for filter_query_number,filter_query in enumerate(filter_queries):
        f = filter_query.split("__")
        if f[1].lower() == 'gt':
            filter_where_list.append("%s > %f" %(f[0], float(f[2])))
        elif f[1].lower() == 'lt':
            filter_where_list.append("%s < %f" %(f[0], float(f[2])))
        elif f[1].lower() == 'gte':
            filter_where_list.append("%s >= %f" %(f[0], float(f[2])))
        elif f[1].lower() == 'lte':
            filter_where_list.append("%s <= %f" %(f[0], float(f[2])))
        elif f[1].lower() in ['bw', 'between']:
            filter_where_list.append("%s BETWEEN %f AND %f" %(f[0], float(f[2]), float(f[3])))
    filter_where_string = " AND ".join(filter_where_list)
    return filter_where_string

#########################################################################
#########################################################################
#########################################################################


def delete_attr_from_summary_table(attr_slug, table=SUMMARY_TABLE_NAME):
    cursor = connection.cursor()
    try:
        cursor.execute("ALTER TABLE %(table)s DROP COLUMN %(col)s" %{'table':table, 'col':attr_slug})
        cache.set('last_summarydb_update',datetime.now(), CACHE_UPDATE_TIMEOUT)
    except DatabaseError:
        # Assume this error is raised because table has been deleted before attributes removed
        pass


def RGBToHTMLColor(rgb_tuple):
    """ convert an (R, G, B) tuple to #RRGGBB """
    return '#%02x%02x%02x' % rgb_tuple



def time_since_last_summary_table_modification(table = SUMMARY_TABLE_NAME):
    """Return timedelta since last modification of summary table."""
    cursor = connection.cursor()
    #print datetime.now()
    try:
        cursor.execute("SELECT max(timestamp) FROM %(table)s" %{'table':table})
        latest_timestamp = cursor.fetchone()[0]
    except DatabaseError:
        generate_base_summary_table(cursor)
        latest_timestamp = None
    if latest_timestamp == None:
        # There are no entries in the summary table...
        latest_timestamp = datetime(MINYEAR, 1, 1)
    try:
        diff = datetime.now() - latest_timestamp
    except TypeError:
        latest_timestamp = datetime.strptime(latest_timestamp, "%Y-%m-%d %H:%M:%S")
        diff = datetime.now() - latest_timestamp
    return diff

def get_attr_list(cursor, table=SUMMARY_TABLE_NAME):
    try:
        # horrid hack
        cursor.execute("SELECT sql FROM sqlite_master WHERE name = '%s'" %table)
        fetchall = cursor.fetchall()
        if not fetchall:
            generate_base_summary_table(cursor)
            cursor.execute("SELECT sql FROM sqlite_master WHERE name = '%s'" %table)
            fetchall = cursor.fetchall()
        return [i for i in fetchall[0][0][15+len(table):-1].split(',')]
    except DatabaseError:
        generate_base_summary_table(cursor)
        cursor.execute("SELECT sql FROM sqlite_master WHERE name = '%s'" %table)
        return [i for i in cursor.fetchall()[0][0][15+len(table):-1].split(',')]

def update_attribute_in_summary_table(attr_slug, table=SUMMARY_TABLE_NAME):
    import h1ds_summary.models
    # TODO: need to get dtype from data source...
    cursor = connection.cursor()

    ## check if attribute already exists.
    attr_list = get_attr_list(cursor, table)
    attribute_instance = h1ds_summary.models.SummaryAttribute.objects.get(slug=attr_slug)
    attr_dtype = attribute_instance.get_value(canonical_shot)[1]

    attr_exists = False
    correct_dtype = False
    for x in attr_list:
        r = x.split()
        if r[0] == attr_slug:
            attr_exists = True
            if r[1].startswith(attr_dtype):
                correct_dtype = True
    if not attr_exists:
        cursor.execute("ALTER TABLE %s ADD COLUMN %s %s" %(table, attr_slug, attr_dtype))
        cache.set('last_summarydb_update',datetime.now(), CACHE_UPDATE_TIMEOUT)
    # TODO: fails for sqlite
    # elif not correct_dtype: 
    #    cursor.execute("ALTER TABLE %s MODIFY COLUMN %s %s" %(table, attr_slug, attr_dtype))
    #    cache.set('last_summarydb_update',datetime.now(), CACHE_UPDATE_TIMEOUT)


def update_single_entry(attribute, shot, value, table=SUMMARY_TABLE_NAME):
    cursor = connection.cursor()
    cursor.execute("UPDATE %s SET %s=%s WHERE shot=%d" %(table, attribute, str(value), shot))
    transaction.commit_unless_managed()
    cache.set('last_summarydb_update',datetime.now(), CACHE_UPDATE_TIMEOUT)
