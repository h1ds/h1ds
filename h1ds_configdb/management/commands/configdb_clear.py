import inspect
from django.core.management.base import BaseCommand
from django.db import models
#from h1ds_configdb.models import ConfigDBFileType, ConfigDBFile, ConfigDBPropertyType, ConfigDBProperty, ConfigDBStringProperty, configdb_type_class_map
import h1ds_configdb.models


class Command(BaseCommand):
    args = ''
    help = 'clear configdb metadata and files.'

    def handle(self, *args, **options):
        #for c in [ConfigDBFileType, ConfigDBFile, ConfigDBPropertyType, ConfigDBProperty, ConfigDBStringProperty]
        
        for name, obj in inspect.getmembers(h1ds_configdb.models):
            if hasattr(obj, "__bases__") and models.Model in obj.__bases__ and obj.__module__ == 'h1ds_configdb.models':
                obj.objects.all().delete()
