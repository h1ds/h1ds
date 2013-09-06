# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'ConfigDBIntProperty'
        db.delete_table('h1ds_configdb_configdbintproperty')

        # Deleting model 'ConfigDBStringProperty'
        db.delete_table('h1ds_configdb_configdbstringproperty')

        # Deleting model 'ConfigDBFloatProperty'
        db.delete_table('h1ds_configdb_configdbfloatproperty')

        # Deleting field 'ConfigDBPropertyType.content_type'
        db.delete_column('h1ds_configdb_configdbpropertytype', 'content_type_id')

        # Adding field 'ConfigDBPropertyType.value_type'
        db.add_column('h1ds_configdb_configdbpropertytype', 'value_type', self.gf('django.db.models.fields.CharField')(default='FL', max_length=2), keep_default=False)

        # Deleting field 'ConfigDBProperty.object_id'
        db.delete_column('h1ds_configdb_configdbproperty', 'object_id')

        # Deleting field 'ConfigDBProperty.content_type'
        db.delete_column('h1ds_configdb_configdbproperty', 'content_type_id')

        # Adding field 'ConfigDBProperty.value_float'
        db.add_column('h1ds_configdb_configdbproperty', 'value_float', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)

        # Adding field 'ConfigDBProperty.value_integer'
        db.add_column('h1ds_configdb_configdbproperty', 'value_integer', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True), keep_default=False)

        # Adding field 'ConfigDBProperty.value_string'
        db.add_column('h1ds_configdb_configdbproperty', 'value_string', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding model 'ConfigDBIntProperty'
        db.create_table('h1ds_configdb_configdbintproperty', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('h1ds_configdb', ['ConfigDBIntProperty'])

        # Adding model 'ConfigDBStringProperty'
        db.create_table('h1ds_configdb_configdbstringproperty', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('h1ds_configdb', ['ConfigDBStringProperty'])

        # Adding model 'ConfigDBFloatProperty'
        db.create_table('h1ds_configdb_configdbfloatproperty', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('h1ds_configdb', ['ConfigDBFloatProperty'])

        # User chose to not deal with backwards NULL issues for 'ConfigDBPropertyType.content_type'
        raise RuntimeError("Cannot reverse this migration. 'ConfigDBPropertyType.content_type' and its values cannot be restored.")

        # Deleting field 'ConfigDBPropertyType.value_type'
        db.delete_column('h1ds_configdb_configdbpropertytype', 'value_type')

        # User chose to not deal with backwards NULL issues for 'ConfigDBProperty.object_id'
        raise RuntimeError("Cannot reverse this migration. 'ConfigDBProperty.object_id' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'ConfigDBProperty.content_type'
        raise RuntimeError("Cannot reverse this migration. 'ConfigDBProperty.content_type' and its values cannot be restored.")

        # Deleting field 'ConfigDBProperty.value_float'
        db.delete_column('h1ds_configdb_configdbproperty', 'value_float')

        # Deleting field 'ConfigDBProperty.value_integer'
        db.delete_column('h1ds_configdb_configdbproperty', 'value_integer')

        # Deleting field 'ConfigDBProperty.value_string'
        db.delete_column('h1ds_configdb_configdbproperty', 'value_string')


    models = {
        'h1ds_configdb.configdbfile': {
            'Meta': {'object_name': 'ConfigDBFile'},
            'dbfile': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
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
        'h1ds_configdb.configdbproperty': {
            'Meta': {'object_name': 'ConfigDBProperty'},
            'configdb_file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['h1ds_configdb.ConfigDBFile']"}),
            'configdb_propertytype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['h1ds_configdb.ConfigDBPropertyType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value_float': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'value_integer': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'value_string': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        'h1ds_configdb.configdbpropertytype': {
            'Meta': {'object_name': 'ConfigDBPropertyType'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'value_type': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        }
    }

    complete_apps = ['h1ds_configdb']
