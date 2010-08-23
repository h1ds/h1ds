from celery.decorators import task

from models import Shot, SummaryAttribute, FloatAttributeInstance, datatype_class_mapping

@task()
def generate_shot(shot_number):
    # remove any Shot with same shot number
    #Shot.objects.filter(shot=shot_number).delete()
    # XXX make a base class, eg, to get rid of all
    #FloatAttributeInstance.objects.filter(shot__shot=shot_number).delete()
    s = Shot()
    s.shot = shot_number
    s.save()
    for summary_attr in SummaryAttribute.objects.all():
        new_attr = datatype_class_mapping[summary_attr.data_type]()
        new_attr.shot = s
        new_attr.attribute = summary_attr
        new_attr.value = summary_attr.get_value(s.shot)
        new_attr.save()
