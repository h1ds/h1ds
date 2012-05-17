import numpy
from django.db import models
from django.template.defaultfilters import slugify

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


class ConfigDBFile(models.Model):
    filename = models.FilePathField()
    filetype = models.ForeignKey(ConfigDBFileType)

class ConfigDBPropertyType(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    slug = models.SlugField()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(ConfigDBPropertyType, self).save(*args, **kwargs)

class ConfigDBBaseProperty(models.Model):
    configdb_file = models.ForeignKey(ConfigDBFile)
    configdb_propertytype = models.ForeignKey(ConfigDBPropertyType)

    class Meta:
        verbose_name_plural = "config db base properties"

    
class ConfigDBStringProperty(ConfigDBBaseProperty):
    value = models.CharField(max_length=256)

    class Meta:
        verbose_name_plural = "config db string properties"

class ConfigDBFloatProperty(ConfigDBBaseProperty):
    value = models.FloatField()

    class Meta:
        verbose_name_plural = "config db float properties"

class ConfigDBIntProperty(ConfigDBBaseProperty):
    value = models.FloatField()

    class Meta:
        verbose_name_plural = "config db integer properties"

configdb_type_class_map = {
    str:ConfigDBStringProperty,
    numpy.float64:ConfigDBFloatProperty,
    int:ConfigDBIntProperty
    }
