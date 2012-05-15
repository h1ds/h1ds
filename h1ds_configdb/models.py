
from django.db import models


class ConfigDBFileType(models.Model):
    name = models.CharField(max_length=256)
    mimetype = models.CharField(max_length=126)
    description = models.TextField()

class ConfigDBFile(models.Model):
    filename = models.FilePathField()
    filetype = models.ForeignKey(ConfigDBFileType)

class ConfigDBPropertyType(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()

class ConfigDBBaseProperty(models.Model):
    configdb_file = models.ForeignKey(ConfigDBFile)
    configdb_propertytype = models.ForeignKey(ConfigDBPropertyType)
    
class ConfigDBStringProperty(ConfigDBBaseProperty):
    value = models.CharField(max_length=256)

configdb_type_class_map = {
    str:ConfigDBStringProperty,
    }
