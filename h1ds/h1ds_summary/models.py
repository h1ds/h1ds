import urllib2
import json

from django.db import models
from h1ds.models import Device
from h1ds_summary.db import SummaryTable

sa_help_text = {
    'slug': "Name of the attribute as it appears in the URL.",
    'name': "Full name of the attribute.",
    'source': "Either URL from H1DS  web service (must start with \
http://) or name of class, e.g. h1nf.KappaH (will use h1ds_summary.attri\
butes.h1nf.KappaH).",
    'description': "Full description of the summary attribute.",
    'is_default': "If true, this attribute will be shown in the default \
list, e.g. for shot summary.",
    'display_order': "When visible, attributes will be displayed from \
left to right with increasing display_order.",
    'format_string': 'How value is to be displayed on website (optional).\
e.g. %.2f will format a float to 2 decimal places.',
}


class SummaryAttribute(models.Model):
    slug = models.SlugField(max_length=100, unique=True,
                            help_text=sa_help_text['slug'])
    name = models.CharField(max_length=255,
                            help_text=sa_help_text['name'])
    source = models.CharField(max_length=255,
                              help_text=sa_help_text['source'])
    description = models.TextField(help_text=sa_help_text['description'])
    is_default = models.BooleanField(default=False, blank=True,
                                     help_text=sa_help_text['is_default'])
    display_order = models.IntegerField(default=1000, blank=False,
                                        help_text=sa_help_text['display_order'])
    format_string = models.CharField(max_length=64,
                                     blank=True,
                                     help_text=sa_help_text['format_string'])
    device = models.ForeignKey(Device, on_delete=models.PROTECT)

    # TODO: optional sqlite datatype (sqlite has dynamic type so it's not strictly required)

    class Meta:
        ordering = ["display_order", "slug"]

        permissions = (
            ("sa_recompute", "Can recompute the summ. att. and update database."),
            ("sa_raw_sql", "Can query database with raw SQL."),
        )

    def save(self, *args, **kwargs):
        super(SummaryAttribute, self).save(*args, **kwargs)
        table = SummaryTable(self.device)
        table.create_attribute(self.slug)
        table.populate_attribute(self.slug)

    def delete(self, *args, **kwargs):
        table = SummaryTable(self.device)
        table.delete_attribute(self.slug)
        super(SummaryAttribute, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.name

    def get_value(self, shot_number):
        # TODO: handle errors better
        if self.source.startswith('http://'):
            try:
                fetch_url = self.source.replace('__shot__', str(shot_number))
                request = urllib2.Request(fetch_url)
                response = json.loads(urllib2.urlopen(request).read())
                return response['data']['value'][0]
            except:
                return None
        else:
            # assume source is inside a module in h1ds_summary.attributes
            # TODO: use a python field on the model
            try:
                split_name = self.source.split('.')
                submodule_name = '.'.join(split_name[:-1])
                module_name = '.'.join(['h1ds_summary.attributes', submodule_name])
                class_name = split_name[-1]
                source_module = __import__(module_name, globals(),
                                           locals(), [class_name], -1)
                source_class = source_module.__getattribute__(class_name)
                # Note: take first element (data), currenltly ignoring data type
                return source_class(shot_number).do_script()[0]
            except:
                return None
