import json
from datetime import timedelta

from celery.decorators import task, periodic_task
from celery.task.schedules import crontab
from django.core.cache import cache
from django.core.urlresolvers import reverse, resolve
from django.db import connection, transaction

from h1ds_summary.models import SummaryAttribute

from h1ds_mdsplus.utils import get_latest_shot
from h1ds_summary.utils import get_latest_shot_from_summary_table, time_since_last_summary_table_modification
from h1ds_summary import SUMMARY_TABLE_NAME, MINIMUM_SUMMARY_TABLE_SHOT


# Time between summary table synchronisations
sync_timedelta = timedelta(minutes=1)
#sync_timedelta = timedelta(seconds=10)

def populate_summary_table(shots, attributes='all', table=SUMMARY_TABLE_NAME):
    cursor=connection.cursor()
    if attributes=='all':
        attributes = SummaryAttribute.objects.all()
    if len(attributes) > 0:
        attr_names = tuple(a.slug for a in attributes)
        attr_name_str = '('+','.join(['shot', ','.join((a.slug for a in attributes))]) + ')'
        for shot in shots:
            values = tuple(str(a.get_value(shot)) for a in attributes)
            values_str = '('+','.join([str(shot), ','.join(values)])+')'
            update_str = ','.join(('%s=%s' %(a, values[ai]) for ai, a in enumerate(attr_names)))
            cursor.execute("INSERT INTO %(table)s %(attrs)s VALUES %(vals)s ON DUPLICATE KEY UPDATE %(update)s" %{'table':table,
                                                                                                                  'attrs':attr_name_str,
                                                                                                                  'vals':values_str,
                                                                                                                  'update':update_str,
                                                                                                                  })
            transaction.commit_unless_managed()

def get_sync_info():
    sync_info = {'do_sync':False,
                 'latest_mds_shot':None,
                 'latest_sql_shot':None,
                 'time_since_last_mod':None,
                 }
    # get time since last summary table modification...
    sync_info['time_since_last_mod'] = time_since_last_summary_table_modification()
    if sync_info['time_since_last_mod'] > sync_timedelta:
        # Check if the latest summary table shot is up to date.
        sync_info['latest_mds_shot'] = get_latest_shot()
        sync_info['latest_sql_shot'] = max(get_latest_shot_from_summary_table(), MINIMUM_SUMMARY_TABLE_SHOT)        
        if sync_info['latest_sql_shot'] < sync_info['latest_mds_shot']:
            sync_info['do_sync'] = True
    return sync_info

# need to run celery in beat mode for periodic tasks (-B), e.g. /manage.py celeryd -v 2 -B -s celery -E -l INFO  
@periodic_task(run_every=sync_timedelta)
def sync_summary_table():
    """Check that the summary table is up to date.

    If the summary table has not been altered since the last sync, check
    that  the latest  shot in  the summary  database matches  the latest
    MDSplus  shot. If  not, backfill  the  summary table  from the  most
    recent MDSplus shot.
    """
    sync_info = get_sync_info()
    if sync_info['do_sync']:
        shot_range = range(sync_info['latest_sql_shot'], sync_info['latest_mds_shot']+1)
        shot_range.reverse()
        populate_summary_table(shot_range)
        


@task()
def generate_shot(shot_number):
    # remove any instances for the shot

    if FloatAttributeInstance.objects.filter(shot__shot=shot_number).count() > 0:
        FloatAttributeInstance.objects.filter(shot__shot=shot_number).delete()
        
    if IntegerAttributeInstance.objects.filter(shot__shot=shot_number).count() > 0:
        IntegerAttributeInstance.objects.filter(shot__shot=shot_number).delete()
        
    if DateTimeAttributeInstance.objects.filter(shot__shot=shot_number).count() > 0:
        DateTimeAttributeInstance.objects.filter(shot__shot=shot_number).delete()

    # remove any Shot with same shot number
    if Shot.objects.filter(shot=shot_number).count() > 0:
        Shot.objects.filter(shot=shot_number).delete()
    
    s = Shot()
    s.shot = shot_number
    s.save()
    for summary_attr in SummaryAttribute.objects.all():
        new_attr = datatype_class_mapping[summary_attr.data_type]()
        new_attr.shot = s
        new_attr.attribute = summary_attr
        new_attr.value = summary_attr.get_value(s.shot)
        new_attr.save()
    cache.delete("latest_summary_shot")
    add_shot_to_single_table(shot_number)

@task()
def update_attribute(shot, summary_attribute):
    """ shot is Shot instance, not shot number"""
    new_attr = summary_attribute.get_att_class()()
    new_attr.shot = shot
    new_attr.attribute = summary_attribute
    new_attr.value = summary_attribute.get_value(shot.shot)
    new_attr.save()

#from h1ds_summary.tasks import generate_shot

#def new_shot_callback(sender, **kwargs):
#    """generate new shot when new_shot_signal is received."""
#    result = generate_shot.delay(kwargs['shot'])

## TODO: hook up to h1ds_signal - where to specify h1ds_signal name? should we have a dedicated new shot signal?
#new_shot_signal.connect(new_shot_callback)

