"""Various utility functions, kept here to keep models.py and views.py tidy."""
from datetime import datetime
from django.db import connection
from django.db.utils import DatabaseError

from h1ds_summary import SUMMARY_TABLE_NAME

def generate_base_summary_table(cursor, table = SUMMARY_TABLE_NAME):
    cursor.execute("CREATE TABLE %(table)s (shot MEDIUMINT UNSIGNED, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)" %{'table':table})    

def time_since_last_summary_table_modification(table = SUMMARY_TABLE_NAME):
    """Return timedelta since last modification of summary table."""
    cursor = connection.cursor()
    cursor.execute("SELECT max(timestamp) FROM %(table)s" %{'table':table})
    latest_timestamp = cursor.fetchone()[0]
    return datetime.now() - latest_timestamp
    
def get_latest_shot_from_summary_table(table = SUMMARY_TABLE_NAME):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT MAX(shot) FROM %(table)s" %{'table':table})
    except DatabaseError:
        generate_base_summary_table(cursor)
        cursor.execute("SELECT MAX(shot) FROM %(table)s" %{'table':table})
        
    latest_shot = cursor.fetchone()
    return latest_shot

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

    
