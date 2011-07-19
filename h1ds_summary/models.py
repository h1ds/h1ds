import urllib2, json
from django.db import models

from h1ds_summary.utils import delete_attr_from_summary_table, update_attribute_in_summary_table
from h1ds_summary.tasks import populate_attribute_task

class SummaryAttribute(models.Model):
    slug = models.SlugField(max_length=100, unique=True,
                            help_text="Name of the attribute as it appears in the URL")
    name = models.CharField(max_length=500,
                            help_text="Full name of the attribute")
    source = models.CharField(max_length=4096,
                              help_text="Either URL from H1DS MDSplus web service (must start with http://) or name of class, e.g. h1nf.KappaH (will use h1ds_summary.attributes.h1nf.KappaH)")

    description = models.TextField()
    is_default = models.BooleanField(default=False,
                                     blank=True,
                                     help_text="If true, this attribute will be shown in the default list, e.g. for shot summary.")

    display_order = models.IntegerField(default=1000,
                                        blank=False,
                                        help_text="When visible, attributes will be displayed from left to right with increasing display_order.")

    class Meta:
        ordering = ["display_order"]

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
            module_name = '.'.join(['h1ds_summary.attributes', '.'.join(split_name[:-1])])
            class_name = split_name[-1]
            source_class = __import__(module_name, globals(), locals(), [class_name], -1).__getattribute__(class_name)
            return source_class(shot_number).do_script()
