# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'SummaryAttribute.full_description'
        db.delete_column('h1ds_summary_summaryattribute', 'full_description')

        # Deleting field 'SummaryAttribute.short_description'
        db.delete_column('h1ds_summary_summaryattribute', 'short_description')

        # Adding field 'SummaryAttribute.description'
        db.add_column('h1ds_summary_summaryattribute', 'description', self.gf('django.db.models.fields.TextField')(default='No description'), keep_default=False)


    def backwards(self, orm):
        
        # We cannot add back in field 'SummaryAttribute.full_description'
        raise RuntimeError(
            "Cannot reverse this migration. 'SummaryAttribute.full_description' and its values cannot be restored.")

        # We cannot add back in field 'SummaryAttribute.short_description'
        raise RuntimeError(
            "Cannot reverse this migration. 'SummaryAttribute.short_description' and its values cannot be restored.")

        # Deleting field 'SummaryAttribute.description'
        db.delete_column('h1ds_summary_summaryattribute', 'description')


    models = {
        'h1ds_summary.datetimeattributeinstance': {
            'Meta': {'object_name': 'DateTimeAttributeInstance'},
            'attribute': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['h1ds_summary.SummaryAttribute']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['h1ds_summary.Shot']"}),
            'value': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
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
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '1000'})
        }
    }

    complete_apps = ['h1ds_summary']
