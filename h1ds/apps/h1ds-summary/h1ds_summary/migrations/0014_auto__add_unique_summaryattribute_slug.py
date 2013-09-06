# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding unique constraint on 'SummaryAttribute', fields ['slug']
        db.create_unique('h1ds_summary_summaryattribute', ['slug'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'SummaryAttribute', fields ['slug']
        db.delete_unique('h1ds_summary_summaryattribute', ['slug'])


    models = {
        'h1ds_summary.summaryattribute': {
            'Meta': {'ordering': "['display_order']", 'object_name': 'SummaryAttribute'},
            'data_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'display_order': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '1000'})
        }
    }

    complete_apps = ['h1ds_summary']
