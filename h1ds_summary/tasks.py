from celery.decorators import task
from django.core.cache import cache

from models import Shot, SummaryAttribute, FloatAttributeInstance, datatype_class_mapping, add_shot_to_single_table, IntegerAttributeInstance, DateTimeAttributeInstance, add_attr_value_to_single_table

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
