import json
from datetime import datetime, timedelta

from celery.decorators import task, periodic_task
from celery.task.schedules import crontab
from django.core.cache import cache
from django.core.urlresolvers import reverse, resolve
from django.db import connection, transaction

from MDSplus import TreeException

from h1ds_summary.utils import get_latest_shot_from_summary_table, time_since_last_summary_table_modification
from h1ds_summary.utils import update_attribute_in_summary_table
from h1ds_summary.utils import CACHE_UPDATE_TIMEOUT
from h1ds_summary import SUMMARY_TABLE_NAME

from h1ds_mdsplus.utils import get_latest_shot

from django.conf import settings

try:
    MINIMUM_SUMMARY_TABLE_SHOT = settings.MINIMUM_SUMMARY_TABLE_SHOT
except AttributeError:
    MINIMUM_SUMMARY_TABLE_SHOT = 1


# Time between summary table synchronisations
sync_timedelta = timedelta(minutes=1)
#sync_timedelta = timedelta(seconds=10)

def populate_summary_table(shots, attributes='all', table=SUMMARY_TABLE_NAME):
    import h1ds_summary.models
    cursor=connection.cursor()
    if attributes=='all':
        attributes = h1ds_summary.models.SummaryAttribute.objects.all()
    if len(attributes) > 0:
        attr_names = tuple(a.slug for a in attributes)
        attr_name_str = '('+','.join(['shot', ','.join((a.slug for a in attributes))]) + ')'
        for shot in shots:
            try:
                values = tuple(str(a.get_value(shot)[0]) for a in attributes)
            except TreeException:
                # assume the shot doesn't exist
                # TODO: more careful treatment of exceptions, distinguish between shot missing and data missing...
                values = tuple("NULL" for a in attributes)
            values_str = '('+','.join([str(shot), ','.join(values)])+')'
            update_str = ','.join(('%s=%s' %(a, values[ai]) for ai, a in enumerate(attr_names)))
            # TODO: can we use INSERT OR UPDATE to avoid duplication?
            cursor.execute("INSERT OR IGNORE INTO %(table)s %(attrs)s VALUES %(vals)s" %{'table':table,
                                                                                         'attrs':attr_name_str,
                                                                                         'vals':values_str,
                                                                                         })
            update_str = update_str + ",timestamp=datetime('now')"
            cursor.execute("UPDATE %(table)s SET %(update)s WHERE shot=%(shot)d" %{'table':table,
                                                                                   'update':update_str,
                                                                                   'shot':shot,
                                                                                   })
            transaction.commit_unless_managed()
            cache.set('last_summarydb_update',datetime.now(), CACHE_UPDATE_TIMEOUT)


@task()
def populate_summary_table_task(shots, attributes='all', table=SUMMARY_TABLE_NAME):
    populate_summary_table(shots, attributes=attributes, table=table)

def get_sync_info():
    sync_info = {'do_sync':False,
                 'latest_mds_shot':None,
                 'latest_sql_shot':None,
                 'time_since_last_mod':None,
                 }
    # get time since last summary table modification...
    sync_info['time_since_last_mod'] = time_since_last_summary_table_modification()
    #print sync_info['time_since_last_mod']
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


def populate_attribute(attr_slug, table=SUMMARY_TABLE_NAME):
    """Update the column for all shots in the summary database."""
    import h1ds_summary.models
    # get summary instance
    attr_instance = h1ds_summary.models.SummaryAttribute.objects.get(slug=attr_slug)
    # get shot list
    cursor = connection.cursor()
    cursor.execute("SELECT shot from %(table)s GROUP BY -shot" %{'table':table})
    shot_list = [int(i[0]) for i in cursor.fetchall()]
    for shot in shot_list:
        value = attr_instance.get_value(shot)[0]
        cursor.execute("UPDATE %(table)s SET %(attr)s=%(val)s WHERE shot=%(shot)d" %{'table':table,
                                                                                     'attr':attr_slug,
                                                                                     'val':value,
                                                                                     'shot':shot})
        transaction.commit_unless_managed()
        cache.set('last_summarydb_update',datetime.now(), CACHE_UPDATE_TIMEOUT)


@task()
def populate_attribute_task(attr_slug, table=SUMMARY_TABLE_NAME):
    populate_attribute(attr_slug, table=table)


#from h1ds_summary.tasks import generate_shot

#def new_shot_callback(sender, **kwargs):
#    """generate new shot when new_shot_signal is received."""
#    result = generate_shot.delay(kwargs['shot'])

## TODO: hook up to h1ds_signal - where to specify h1ds_signal name? should we have a dedicated new shot signal?
#new_shot_signal.connect(new_shot_callback)
