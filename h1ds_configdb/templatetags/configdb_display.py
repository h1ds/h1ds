from django import template

register = template.Library()

@register.inclusion_tag('h1ds_configdb/configdb_display.html')
def show_configfile(configfile):
    tag_data = {'name': configfile.filename}
    tag_data['properties'] = []
    for p in configfile.configdbproperty_set.all():
        tag_data['properties'].append([p.configdb_propertytype.name, p.value.value])
    return tag_data
