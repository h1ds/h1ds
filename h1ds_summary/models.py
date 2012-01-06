import urllib2, json
from django.db import models

from h1ds_summary.utils import delete_attr_from_summary_table
from h1ds_summary.utils import update_attribute_in_summary_table
from h1ds_summary.tasks import populate_attribute_task

sa_help_text={
    'slug':"Name of the attribute as it appears in the URL.",
    'name':"Full name of the attribute.",
    'source':"Either URL from H1DS MDSplus web service (must start with \
http://) or name of class, e.g. h1nf.KappaH (will use h1ds_summary.attri\
butes.h1nf.KappaH).",
    'description':"Full description of the summary attribute.",
    'is_default':"If true, this attribute will be shown in the default \
list, e.g. for shot summary.",
    'display_order':"When visible, attributes will be displayed from \
left to right with increasing display_order."
    }

class SummaryAttribute(models.Model):
    slug = models.SlugField(max_length=100, unique=True, 
                            help_text=sa_help_text['slug'])
    name = models.CharField(max_length=500, 
                            help_text=sa_help_text['name'])
    source = models.CharField(max_length=4096,
                              help_text=sa_help_text['source'])
    description = models.TextField(help_text=sa_help_text['description'])
    is_default = models.BooleanField(default=False, blank=True,
                                     help_text=sa_help_text['is_default'])
    display_order = models.IntegerField(default=1000, blank=False,
                                        help_text=sa_help_text['display_order'])

    class Meta:
        ordering = ["display_order"]

        permissions = (
            ("recompute_summaryattribute", "Can recompute the summary attribute and update the database."),
            )
    
    def save(self, *args, **kwargs):
        super(SummaryAttribute, self).save(*args, **kwargs)
        update_attribute_in_summary_table(self.slug)
        populate_attribute_task.delay(self.slug)

    def delete(self, *args, **kwargs):
        delete_attr_from_summary_table(self.slug)
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
                value = response['data']
                dtype = response['summary_dtype']
                if value == None:
                    value = 'NULL'
                return (value, dtype)
            except:
                return ('NULL', 'NULL')
        else:
            # assume source is inside a module in h1ds_summary.attributes
            split_name = self.source.split('.')
            submodule_name = '.'.join(split_name[:-1])
            module_name = '.'.join(['h1ds_summary.attributes', submodule_name])
            class_name = split_name[-1]
            source_module = __import__(module_name, globals(), 
                                       locals(), [class_name], -1)
            source_class = source_module.__getattribute__(class_name)
            return source_class(shot_number).do_script()


