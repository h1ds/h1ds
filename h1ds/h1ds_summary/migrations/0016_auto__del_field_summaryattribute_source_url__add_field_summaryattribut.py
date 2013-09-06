# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'SummaryAttribute.source_url'
        db.delete_column('h1ds_summary_summaryattribute', 'source_url')

        # Adding field 'SummaryAttribute.source'
        db.add_column('h1ds_summary_summaryattribute', 'source', self.gf('django.db.models.fields.CharField')(default='changeme', max_length=4096), keep_default=False)


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'SummaryAttribute.source_url'
        raise RuntimeError("Cannot reverse this migration. 'SummaryAttribute.source_url' and its values cannot be restored.")

        # Deleting field 'SummaryAttribute.source'
        db.delete_column('h1ds_summary_summaryattribute', 'source')


    models = {
        'h1ds_summary.summaryattribute': {
            'Meta': {'ordering': "['display_order']", 'object_name': 'SummaryAttribute'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'display_order': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '4096'})
        }
    }

    complete_apps = ['h1ds_summary']
