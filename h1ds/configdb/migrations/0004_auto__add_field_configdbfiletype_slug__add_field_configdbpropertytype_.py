# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'ConfigDBFileType.slug'
        db.add_column('h1ds_configdb_configdbfiletype', 'slug', self.gf('django.db.models.fields.SlugField')(default='slug', max_length=50, db_index=True), keep_default=False)

        # Adding field 'ConfigDBPropertyType.slug'
        db.add_column('h1ds_configdb_configdbpropertytype', 'slug', self.gf('django.db.models.fields.SlugField')(default='slug', max_length=50, db_index=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'ConfigDBFileType.slug'
        db.delete_column('h1ds_configdb_configdbfiletype', 'slug')

        # Deleting field 'ConfigDBPropertyType.slug'
        db.delete_column('h1ds_configdb_configdbpropertytype', 'slug')


    models = {
        'h1ds_configdb.configdbbaseproperty': {
            'Meta': {'object_name': 'ConfigDBBaseProperty'},
            'configdb_file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['h1ds_configdb.ConfigDBFile']"}),
            'configdb_propertytype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['h1ds_configdb.ConfigDBPropertyType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'h1ds_configdb.configdbfile': {
            'Meta': {'object_name': 'ConfigDBFile'},
            'filename': ('django.db.models.fields.FilePathField', [], {'max_length': '100'}),
            'filetype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['h1ds_configdb.ConfigDBFileType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'h1ds_configdb.configdbfiletype': {
            'Meta': {'object_name': 'ConfigDBFileType'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '126'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'h1ds_configdb.configdbfloatproperty': {
            'Meta': {'object_name': 'ConfigDBFloatProperty', '_ormbases': ['h1ds_configdb.ConfigDBBaseProperty']},
            'configdbbaseproperty_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['h1ds_configdb.ConfigDBBaseProperty']", 'unique': 'True', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        'h1ds_configdb.configdbintproperty': {
            'Meta': {'object_name': 'ConfigDBIntProperty', '_ormbases': ['h1ds_configdb.ConfigDBBaseProperty']},
            'configdbbaseproperty_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['h1ds_configdb.ConfigDBBaseProperty']", 'unique': 'True', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        'h1ds_configdb.configdbpropertytype': {
            'Meta': {'object_name': 'ConfigDBPropertyType'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'h1ds_configdb.configdbstringproperty': {
            'Meta': {'object_name': 'ConfigDBStringProperty', '_ormbases': ['h1ds_configdb.ConfigDBBaseProperty']},
            'configdbbaseproperty_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['h1ds_configdb.ConfigDBBaseProperty']", 'unique': 'True', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['h1ds_configdb']
