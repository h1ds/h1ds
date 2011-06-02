import json
from datetime import timedelta

from celery.decorators import task, periodic_task
from celery.task.schedules import crontab
from django.core.cache import cache
from django.core.urlresolvers import reverse, resolve

from h1ds_summary.models import Shot, SummaryAttribute, FloatAttributeInstance, datatype_class_mapping, add_shot_to_single_table, IntegerAttributeInstance, DateTimeAttributeInstance, add_attr_value_to_single_table

from h1ds_mdsplus.utils import get_latest_shot
from h1ds_summary.utils import get_latest_shot_from_summary_table, time_since_last_summary_table_modification


# Time between summary table synchronisations
sync_timedelta = timedelta(minutes=1)

# need to run celery in beat mode for periodic tasks (-B), e.g. /manage.py celeryd -v 2 -B -s celery -E -l INFO  
@periodic_task(run_every=sync_timedelta)
def sync_summary_table():
    """Check that the summary table is up to date.

    If the summary table has not been altered since the last sync, check
    that  the latest  shot in  the summary  database matches  the latest
    MDSplus  shot. If  not, backfill  the  summary table  from the  most
    recent MDSplus shot.
    """
    
    print "getting latest MDSplus shot..."
    latest_shot = get_latest_shot()
    print latest_shot
    print "... latest SQL shot"
    latest_sql_shot = get_latest_shot_from_summary_table()
    print latest_sql_shot
    print sync_timedelta
    print 'latest_timestamp, ', time_since_last_summary_table_modification()


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
