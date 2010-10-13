# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'SummaryAttribute.is_default'
        db.add_column('h1ds_summary_summaryattribute', 'is_default', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'SummaryAttribute.is_default'
        db.delete_column('h1ds_summary_summaryattribute', 'is_default')


    models = {
        'h1ds_summary.floatattributeinstance': {
            'Meta': {'object_name': 'FloatAttributeInstance'},
            'attribute': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['h1ds_summary.SummaryAttribute']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['h1ds_summary.Shot']"}),
            'value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'h1ds_summary.integerattributeinstance': {
            'Meta': {'object_name': 'IntegerAttributeInstance'},
            'attribute': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['h1ds_summary.SummaryAttribute']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['h1ds_summary.Shot']"}),
            'value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'h1ds_summary.shot': {
            'Meta': {'object_name': 'Shot'},
            'shot': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        'h1ds_summary.summaryattribute': {
            'Meta': {'object_name': 'SummaryAttribute'},
            'data_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'default_max': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'default_min': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'display_format': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        }
    }

    complete_apps = ['h1ds_summary']
