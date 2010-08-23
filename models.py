import subprocess, shlex, uuid
from django.db import models

from h1ds_interface.signals import new_shot_signal

DATATYPE_CHOICES = (
    ('F', 'Float'),
    ('I', 'Integer'),
    ('D', 'Date and time'),
    ('T', 'Text'),
    )

datatype_python = {
    'F':float,
    }


class FloatAttributeInstance(models.Model):
    shot = models.ForeignKey("Shot")
    attribute = models.ForeignKey("SummaryAttribute")
    value = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.shot) + ' / ' + self.attribute.slug + ' / ' + unicode(self.value)

datatype_class_mapping = {
    'F':FloatAttributeInstance,
    }

class SummaryAttribute(models.Model):
    slug = models.SlugField(max_length=100, help_text="Name of the attribute as it appears in the URL")
    name = models.CharField(max_length=500, help_text="Full name of the attribute")
    source = models.CharField(max_length=1000, help_text="Path to script on the filesystem which takes a shot number as a single argument and returns the attribute value")
    description = models.TextField()
    data_type = models.CharField(max_length=1, choices=DATATYPE_CHOICES, help_text="Data type used to store attribute in database")

    def __unicode__(self):
        return self.name

    def get_att_class(self):
        return datatype_class_mapping[self.data_type]

    def get_datatype(self):
        return datatype_python[self.data_type]

    def get_instances(self):
        return self.get_att_class().objects.filter(attribute=self)
    
    def delete_instances(self):
        self.get_instances().delete()

    def get_value(self, shot_number):
        # we write to a temp file in the filesystem rather than give webserver privs to pipe
        tmpname = '/tmp/'+uuid.uuid4().hex
        sub = subprocess.call(self.source+' '+str(shot_number)+' > %s' %tmpname, shell=True)
        f = open(tmpname)
        data = f.read()
        f.close()
        sub = subprocess.call('/bin/rm %s' %tmpname, shell=True)        
        if data.strip().lower() in ['null', 'none']:
            return None
        else:
            return datatype_python[self.data_type](data)

    def _get_value(self, shot_number):
        # we write to a temp file in the filesystem rather than give webserver privs to pipe
        tmpname = '/tmp/'+uuid.uuid4().hex
        sub = subprocess.call('/home/datasys/code/test/dummy_data.py'+' '+str(shot_number)+' > %s' %tmpname, shell=True)
        f = open(tmpname)
        data = f.read()
        f.close()
        sub = subprocess.call('/bin/rm %s' %tmpname, shell=True)        
        if data.strip().lower() in ['null', 'none']:
            return None
        else:
            return datatype_python[self.data_type](data)


class Shot(models.Model):
    shot = models.IntegerField(primary_key=True)

    def __unicode__(self):
        return unicode(self.shot)


from h1ds_summary.tasks import generate_shot

def new_shot_callback(sender, **kwargs):
    """generate new shot when new_shot_signal is received."""
    result = generate_shot.delay(kwargs['shot'])

new_shot_signal.connect(new_shot_callback)
