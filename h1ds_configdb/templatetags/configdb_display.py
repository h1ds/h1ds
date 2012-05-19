import os
from django import template

register = template.Library()

@register.inclusion_tag('h1ds_configdb/configdb_display.html')
def show_configfile(configfile):
    tag_data = {'name': os.path.basename(configfile.filename)}
    ## TODO: this is a hack. fix the filename, URL path properly
    tag_data['file_url'] = '/media/configdb/'+tag_data['name']
    tag_data['properties'] = []
    for p in configfile.configdbproperty_set.all():
        tag_data['properties'].append([p.configdb_propertytype.name, p.value.value])
    return tag_data
