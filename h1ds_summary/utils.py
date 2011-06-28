"""Various utility functions, kept here to keep models.py and views.py tidy."""
from datetime import datetime, MINYEAR
from colorsys import hsv_to_rgb

from django.db import connection, transaction
from django.db.utils import DatabaseError

from h1ds_summary import SUMMARY_TABLE_NAME
import h1ds_summary.models 


def generate_base_summary_table(cursor, table = SUMMARY_TABLE_NAME):
    attrs = h1ds_summary.models.SummaryAttribute.objects.all()
    attr_string = ",".join(("%s %s" %(a.name, a.get_value(0)[1]) for a in attrs))
    if connection.vendor == 'sqlite':
        cols = ["shot MEDIUMINT UNSIGNED PRIMARY KEY",
                "timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP"]
    else:
        cols = ["shot MEDIUMINT UNSIGNED PRIMARY KEY",
                "timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"]
    if attr_string != "":
        cols.append(attr_string)
    col_str = ','.join(cols)
    cursor.execute("CREATE TABLE %(table)s (%(cols)s)" %{'table':table, 'cols':col_str})    

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
    cursor.execute("ALTER TABLE %(table)s DROP COLUMN %(col)s" %{'table':table, 'col':attr_slug})
    

def RGBToHTMLColor(rgb_tuple):
    """ convert an (R, G, B) tuple to #RRGGBB """
    return '#%02x%02x%02x' % rgb_tuple



def time_since_last_summary_table_modification(table = SUMMARY_TABLE_NAME):
    """Return timedelta since last modification of summary table."""
    cursor = connection.cursor()
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
    

    

def update_attribute_in_summary_table(attr_slug, table=SUMMARY_TABLE_NAME):
    # TODO: need to get dtype from data source...
    cursor = connection.cursor()
    ## check if attribute already exists.
    try:
        if connection.vendor == 'sqlite':
            ## horrid hack
            cursor.execute("SELECT sql FROM sqlite_master WHERE name = '%s'" %table)
            attr_list = [i for i in cursor.fetchall()[0][0][15+len(table):-1].split(',')]
        else:
            cursor.execute("DESCRIBE %s" %table)
            attr_list = cursor.fetchall()
    except DatabaseError:
        # table needs to be created
        generate_base_summary_table(cursor)
        cursor.execute("DESCRIBE %s" %table)        
    attribute_instance = h1ds_summary.models.SummaryAttribute.objects.get(slug=attr_slug)
    #latest_shot = get_latest_shot_from_summary_table()
    attr_dtype = attribute_instance.get_value(0)[1]

    attr_exists = False
    correct_dtype = False
    for r in attr_list:
        if r[0] == attr_slug:
            attr_exists = True
            if r[1].startswith(attr_dtype):
                correct_dtype = True
    if not attr_exists:
        cursor.execute("ALTER TABLE %s ADD COLUMN %s %s" %(table, attr_slug, attr_dtype))
    elif not correct_dtype:
        cursor.execute("ALTER TABLE %s MODIFY COLUMN %s %s" %(table, attr_slug, attr_dtype))

