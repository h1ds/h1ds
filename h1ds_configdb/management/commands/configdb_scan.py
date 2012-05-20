"""
Scan files in settings.H1DS_CONFIGDB_DIR for metadata using
the settings.H1DS_CONFIGDB_METADATA_FUNCTION function

If the file provides metadata, copy the file across to MEDIA_ROOT
in the subdirectory h1ds_configdb.CONFIGDB_SUBFOLDER

Currently there is no check whether the file already exists. For now, 
the expected usage is to clear the configdb using the configdb_clear 
management function, and then repopulate using configdb_scan. More 
intelligent file handling might be added at a later date.
"""
import os
import shutil
import random

from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File

from h1ds_configdb.models import ConfigDBFileType, ConfigDBFile, ConfigDBPropertyType, ConfigDBProperty, ConfigDBStringProperty, configdb_type_class_map
from h1ds_configdb import CONFIGDB_SUBFOLDER


CONFIGDB_PATH = os.path.join(settings.MEDIA_ROOT, CONFIGDB_SUBFOLDER)
metadata_scanner = settings.H1DS_CONFIGDB_METADATA_FUNCTION

class Command(BaseCommand):
    args = ''
    help = 'Scan configdb directory for metadata'

    def handle(self, *args, **options):
        if not os.path.exists(CONFIGDB_PATH):
            os.mkdir(CONFIGDB_PATH)

        failed = 0
        worked = 0
        for root, dirs, files in os.walk(settings.H1DS_CONFIGDB_DIR):
            for fn in [i for i in files]:# if random.random() > 0.9]:
                full_filename = os.path.join(root, fn)
                try:
                    filetype, mimetype, metadata = metadata_scanner(full_filename)

                    # If there is no filetype model instance for this filetype, create one.
                    filetype_instance, filetype_created = ConfigDBFileType.objects.get_or_create(name=filetype, defaults={'mimetype':mimetype})
                    if not filetype_created:
                        # make sure the mimetype here is the same as that stored in database.
                        if filetype_instance.mimetype != mimetype:
                            raise ValueError('wrong mimetype')
                    
                    
                    #configdbfile_instance, configdbfile_created = ConfigDBFile.objects.get_or_create(filename=full_filename, defaults={'filetype':filetype_instance})
                    configdbfile_instance, configdbfile_created = ConfigDBFile.objects.get_or_create(dbfile=File(open(full_filename)), defaults={'filetype':filetype_instance})

                    if True:#configdbfile_created:
                        for (k,v) in metadata.items():
                            if type(v) in configdb_type_class_map.keys() and k not in ['filename','filetype']:
                                property_value_model=configdb_type_class_map[type(v)]
                                property_value_content_type = ContentType.objects.get_for_model(property_value_model)

                                #propertytype_instance, propertytype_created = ConfigDBPropertyType.objects.get_or_create(name=k, defaults={'description':'No description'})                                
                                propertytype_instance, propertytype_created = ConfigDBPropertyType.objects.get_or_create(name=k, content_type=property_value_content_type, defaults={'description':'No description'})                                

                                new_property_value = property_value_model(value=v)
                                new_property_value.save()
                                
                                newproperty = ConfigDBProperty(configdb_file=configdbfile_instance, configdb_propertytype=propertytype_instance , value=new_property_value)
                                #newproperty = ConfigDBProperty(configdb_file=configdbfile_instance, configdb_propertytype=propertytype_instance , object_id=new_property_value.id)
                                newproperty.save()
                                
                            else:
                                #self.stdout.write(str(k)+": "+str(type(v))+'\n')
                                pass
                    #shutil.copy(full_filename, CONFIGDB_PATH)
                    worked +=1
                    #self.stdout.write("    worked: %s\n" %full_filename)
                except NotImplementedError:
                    failed +=1
                    self.stdout.write("*** failed: %s\n" %full_filename)

        self.stdout.write("managed to grab metadata from %d of %d files (%.2f%%)\n" %(worked, worked+failed, 100.*worked/(worked+failed)))

                
