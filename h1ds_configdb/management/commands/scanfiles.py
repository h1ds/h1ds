import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from h1ds_configdb.models import ConfigDBFileType, ConfigDBFile, ConfigDBPropertyType, ConfigDBStringProperty, configdb_type_class_map

metadata_scanner = settings.H1DS_CONFIGDB_METADATA_FUNCTION

class Command(BaseCommand):
    args = ''
    help = 'Scan configdb directory for metadata'

    def handle(self, *args, **options):
        failed = 0
        worked = 0
        for root, dirs, files in os.walk(settings.H1DS_CONFIGDB_DIR):
            for fn in files:
                try:
                    full_filename = os.path.join(root, fn)
                    filetype, mimetype, metadata = metadata_scanner(full_filename)
                    
                    # If there is no filetype model instance for this filetype, create one.
                    filetype_instance, filetype_created = ConfigDBFileType.objects.get_or_create(name=filetype, defaults={'mimetype':mimetype})
                    if not filetype_created:
                        # make sure the mimetype here is the same as that stored in database.
                        if filetype_instance.mimetype != mimetype:
                            raise ValueError('wrong mimetype')
                    
                    
                    configdbfile_instance, configdbfile_created = ConfigDBFile.objects.get_or_create(filename=full_filename, defaults={'filetype':filetype_instance})
                    if configdbfile_created:
                        for (k,v) in metadata.items():
                            if type(v) in configdb_type_class_map.keys():
                                propertytype_instance, propertytype_created = ConfigDBPropertyType.objects.get_or_create(name=k, defaults={'description':'No description'})
                                

                                property_model=configdb_type_class_map[type(v)]
                                new_property = property_model(configdb_file=configdbfile_instance, configdb_propertytype=propertytype_instance, value=v)
                                new_property.save()
                    worked +=1
                except:
                    failed +=1
        self.stdout.write("managed to grab metadata from %d of %d files (%.2f%%)\n" %(worked, worked+failed, 100.*worked/(worked+failed)))

                
