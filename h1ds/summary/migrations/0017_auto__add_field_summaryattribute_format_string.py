# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'SummaryAttribute.format_string'
        db.add_column('h1ds_summary_summaryattribute', 'format_string', self.gf('django.db.models.fields.CharField')(default='', max_length=64, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'SummaryAttribute.format_string'
        db.delete_column('h1ds_summary_summaryattribute', 'format_string')


    models = {
        'h1ds_summary.summaryattribute': {
            'Meta': {'ordering': "['display_order']", 'object_name': 'SummaryAttribute'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'display_order': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'format_string': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '4096'})
        }
    }

    complete_apps = ['h1ds_summary']
