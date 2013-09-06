# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'SummaryAttribute.data_type'
        db.delete_column('h1ds_summary_summaryattribute', 'data_type')


    def backwards(self, orm):
        
        # We cannot add back in field 'SummaryAttribute.data_type'
        raise RuntimeError(
            "Cannot reverse this migration. 'SummaryAttribute.data_type' and its values cannot be restored.")


    models = {
        'h1ds_summary.summaryattribute': {
            'Meta': {'ordering': "['display_order']", 'object_name': 'SummaryAttribute'},
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
