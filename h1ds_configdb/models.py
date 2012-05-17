import numpy
from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

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

class ConfigDBFile(models.Model):
    filename = models.FilePathField()
    filetype = models.ForeignKey(ConfigDBFileType)

    
    #def get_properties(self):
    #    """
    #    This is a bit messy, reconsider how best to do the 
    #    reverse lookup of subclasses...
    #    """
    #    props = []
    #    for cl in [ConfigDBStringProperty, ConfigDBIntProperty, ConfigDBFloatProperty]:
    #        for p in cl.objects.filter(configdb_file = self):
    #            props.append([p.configdb_propertytype.name,p.value])
    #    return props

configdb_type_class_map = {
    str:ConfigDBStringProperty,
    numpy.float64:ConfigDBFloatProperty,
    int:ConfigDBIntProperty
    }
