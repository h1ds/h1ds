# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'IntegerAttributeInstance'
        db.delete_table('h1ds_summary_integerattributeinstance')

        # Deleting model 'DateTimeAttributeInstance'
        db.delete_table('h1ds_summary_datetimeattributeinstance')

        # Deleting model 'Shot'
        db.delete_table('h1ds_summary_shot')

        # Deleting model 'FloatAttributeInstance'
        db.delete_table('h1ds_summary_floatattributeinstance')

        # Adding field 'SummaryAttribute.display_order'
        db.add_column('h1ds_summary_summaryattribute', 'display_order', self.gf('django.db.models.fields.IntegerField')(default=1000), keep_default=False)


    def backwards(self, orm):
        
        # Adding model 'IntegerAttributeInstance'
        db.create_table('h1ds_summary_integerattributeinstance', (
            ('attribute', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['h1ds_summary.SummaryAttribute'])),
            ('shot', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['h1ds_summary.Shot'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('h1ds_summary', ['IntegerAttributeInstance'])

        # Adding model 'DateTimeAttributeInstance'
        db.create_table('h1ds_summary_datetimeattributeinstance', (
            ('attribute', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['h1ds_summary.SummaryAttribute'])),
            ('shot', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['h1ds_summary.Shot'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('h1ds_summary', ['DateTimeAttributeInstance'])

        # Adding model 'Shot'
        db.create_table('h1ds_summary_shot', (
            ('shot', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
        ))
        db.send_create_signal('h1ds_summary', ['Shot'])

        # Adding model 'FloatAttributeInstance'
        db.create_table('h1ds_summary_floatattributeinstance', (
            ('attribute', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['h1ds_summary.SummaryAttribute'])),
            ('shot', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['h1ds_summary.Shot'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('h1ds_summary', ['FloatAttributeInstance'])

        # Deleting field 'SummaryAttribute.display_order'
        db.delete_column('h1ds_summary_summaryattribute', 'display_order')


    models = {
        'h1ds_summary.summaryattribute': {
            'Meta': {'object_name': 'SummaryAttribute'},
            'data_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'display_order': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '1000'})
        }
    }

    complete_apps = ['h1ds_summary']
