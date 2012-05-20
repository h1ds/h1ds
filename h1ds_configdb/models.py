import os
import numpy
from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError
from django.conf import settings

from h1ds_configdb import CONFIGDB_SUBFOLDER

class ConfigDBFileType(models.Model):
    name = models.CharField(max_length=256)
    mimetype = models.CharField(max_length=126)
    description = models.TextField()
    slug = models.SlugField()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(ConfigDBFileType, self).save(*args, **kwargs)

class ConfigDBPropertyType(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    slug = models.SlugField()
    content_type = models.ForeignKey(ContentType)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(ConfigDBPropertyType, self).save(*args, **kwargs)



class ConfigDBProperty(models.Model):
    configdb_file = models.ForeignKey("ConfigDBFile")
    configdb_propertytype = models.ForeignKey(ConfigDBPropertyType)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    value = generic.GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        verbose_name_plural = "config db properties"

    ## override save, if content type is different to that of configdb_propertytype, than raise an exception.
    def save(self, *args, **kwargs):
        if self.content_type != self.configdb_propertytype.content_type:
            raise ValidationError
        super(ConfigDBProperty, self).save(*args,**kwargs)
            

class ConfigDBStringProperty(models.Model):
    value = models.CharField(max_length=256)

    class Meta:
        verbose_name_plural = "config db string properties"

class ConfigDBFloatProperty(models.Model):
    value = models.FloatField()

    class Meta:
        verbose_name_plural = "config db float properties"

class ConfigDBIntProperty(models.Model):
    value = models.IntegerField()

    class Meta:
        verbose_name_plural = "config db integer properties"

def configdb_filename(instance, filename):
    split_path = filename.split('/')
    n_dir_conf = len(settings.H1DS_CONFIGDB_DIR.split('/'))
    
    new_paths = [CONFIGDB_SUBFOLDER]
    new_paths.extend(split_path[n_dir_conf:])
    
    return os.path.join(*new_paths)

class ConfigDBFile(models.Model):
    dbfile = models.FileField(upload_to=configdb_filename)
    filetype = models.ForeignKey(ConfigDBFileType)

configdb_type_class_map = {
    str:ConfigDBStringProperty,
    numpy.float64:ConfigDBFloatProperty,
    int:ConfigDBIntProperty
    }
