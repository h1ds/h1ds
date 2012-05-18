import os

from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from h1ds_configdb.models import ConfigDBFileType, ConfigDBFile, ConfigDBPropertyType, ConfigDBProperty, ConfigDBStringProperty, configdb_type_class_map

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
                #if True:
                    
                    full_filename = os.path.join(root, fn)
                    filetype, mimetype, metadata = metadata_scanner(full_filename)
                    
                    # If there is no filetype model instance for this filetype, create one.
                    filetype_instance, filetype_created = ConfigDBFileType.objects.get_or_create(name=filetype, defaults={'mimetype':mimetype})
                    if not filetype_created:
                        # make sure the mimetype here is the same as that stored in database.
                        if filetype_instance.mimetype != mimetype:
                            raise ValueError('wrong mimetype')
                    
                    
                    configdbfile_instance, configdbfile_created = ConfigDBFile.objects.get_or_create(filename=full_filename, defaults={'filetype':filetype_instance})
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
                                self.stdout.write(str(k)+": "+str(type(v))+'\n')
                    worked +=1
                except NotImplementedError:
                    failed +=1
        self.stdout.write("managed to grab metadata from %d of %d files (%.2f%%)\n" %(worked, worked+failed, 100.*worked/(worked+failed)))

                
