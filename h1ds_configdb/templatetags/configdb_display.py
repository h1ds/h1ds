from django import template

register = template.Library()

@register.inclusion_tag('h1ds_configdb/configdb_display.html')
def show_configfile(configfile):
    tag_data = {'name': configfile.filename}
    tag_data['properties'] = configfile.get_properties()
    return tag_data
