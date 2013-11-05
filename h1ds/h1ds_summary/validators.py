# coding=utf-8

from django.core.exceptions import ValidationError

# TODO: figure out regexes for shot and attribute slugs and use standard django regex validator


def shotslug_validator(value):
    shot_str = value.lower()
    if shot_str == 'all':
        return None

    # Now split the query into the separate components
    # i.e. "123+345-350" -> ["123", "345-350"]
    try:
        shot_components = shot_str.split('+')
    except:
        raise ValidationError('Cannot split string into 1+2+3-10+20 etc')

    for shot_comp in shot_components:
        if shot_comp.startswith('last'):
            try:
                int(shot_comp[4:])
            except:
                raise ValidationError('"last" should be followed by an integer, e.g. last10')
        elif '-' in shot_comp:
            try:
                map(int, shot_comp.split('-'))
            except:
                raise ValidationError('Hyphens should be used to separate shot numbers, denoting a range of shots. e.g. 10-20')
        else:
            try:
                int(shot_comp)
            except:
                raise ValidationError('Cannot cast {} to an integer'.format(shot_comp))


# TODO: how to configure validator for a given device - so we know which attributes are valid?
def attributeslug_validator(value):
    pass

