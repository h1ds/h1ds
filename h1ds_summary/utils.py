"""Various utility functions, kept here to keep models.py and views.py tidy."""
from datetime import datetime, MINYEAR
from django.db import connection
from django.db.utils import DatabaseError

from h1ds_summary import SUMMARY_TABLE_NAME
import h1ds_summary.models 


def generate_base_summary_table(cursor, table = SUMMARY_TABLE_NAME):
    attrs = h1ds_summary.models.SummaryAttribute.objects.all()
    attr_string = ",".join(("%s %s" %(a.name, h1ds_summary.models.sql_type_codes[a.data_type]) for a in attrs))
    cols = ("shot MEDIUMINT UNSIGNED PRIMARY KEY",
            "timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
            attr_string,
            )
    col_str = ','.join(cols)
    cursor.execute("CREATE TABLE %(table)s (%(cols)s)" %{'table':table, 'cols':col_str})    

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
    
def get_latest_shot_from_summary_table(table = SUMMARY_TABLE_NAME):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT MAX(shot) FROM %(table)s" %{'table':table})
    except DatabaseError:
        generate_base_summary_table(cursor)
        cursor.execute("SELECT MAX(shot) FROM %(table)s" %{'table':table})
        
    latest_shot = cursor.fetchone()[0]
    return latest_shot

