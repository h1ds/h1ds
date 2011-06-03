"""Various utility functions, kept here to keep models.py and views.py tidy."""
from datetime import datetime, MINYEAR
from colorsys import hsv_to_rgb

from django.db import connection
from django.db.utils import DatabaseError

from h1ds_summary import SUMMARY_TABLE_NAME, SQL_TYPE_CODES
import h1ds_summary.models 


def generate_base_summary_table(cursor, table = SUMMARY_TABLE_NAME):
    attrs = h1ds_summary.models.SummaryAttribute.objects.all()
    attr_string = ",".join(("%s %s" %(a.name, SQL_TYPE_CODES[a.data_type]) for a in attrs))
    cols = ("shot MEDIUMINT UNSIGNED PRIMARY KEY",
            "timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
            attr_string,
            )
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

def parse_shot_str(shot_str, table=SUMMARY_TABLE_NAME):
    """Parse the URL path component corresponding to the requested shots."""

    # Put the shot string into lower case so we can easily match 'last'
    shot_str = shot_str.lower()
    
    if 'last' in shot_str:
        # Only touch the database if we need to...
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
    return datetime.now() - latest_timestamp
    

def update_attribute_in_summary_table(attr_name, attr_type, table=SUMMARY_TABLE_NAME):
    cursor = connection.cursor()
    ## check if attribute already exists.
    try:
        cursor.execute("DESCRIBE %s" %table)
    except DatabaseError:
        # table needs to be created
        generate_base_summary_table(cursor)
        cursor.execute("DESCRIBE %s" %table)        
    attr_exists = False
    correct_type = False
    for r in cursor.fetchall():
        if r[0] == attr_name:
            attr_exists = True
            if r[1].startswith(attr_type):
                correct_type = True
    if not attr_exists:
        cursor.execute("ALTER TABLE %s ADD COLUMN %s %s" %(table, attr_name, attr_type))
    elif not correct_type:
        cursor.execute("ALTER TABLE %s MODIFY COLUMN %s %s" %(table, attr_name, attr_type))
