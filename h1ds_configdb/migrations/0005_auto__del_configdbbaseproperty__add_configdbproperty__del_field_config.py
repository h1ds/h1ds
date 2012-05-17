# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'ConfigDBBaseProperty'
        db.delete_table('h1ds_configdb_configdbbaseproperty')

        # Adding model 'ConfigDBProperty'
        db.create_table('h1ds_configdb_configdbproperty', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('configdb_file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['h1ds_configdb.ConfigDBFile'])),
            ('configdb_propertytype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['h1ds_configdb.ConfigDBPropertyType'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('h1ds_configdb', ['ConfigDBProperty'])

        # Deleting field 'ConfigDBIntProperty.configdbbaseproperty_ptr'
        db.delete_column('h1ds_configdb_configdbintproperty', 'configdbbaseproperty_ptr_id')

        # Adding field 'ConfigDBIntProperty.id'
        db.add_column('h1ds_configdb_configdbintproperty', 'id', self.gf('django.db.models.fields.AutoField')(default=1, primary_key=True), keep_default=False)

        # Changing field 'ConfigDBIntProperty.value'
        db.alter_column('h1ds_configdb_configdbintproperty', 'value', self.gf('django.db.models.fields.IntegerField')())

        # Deleting field 'ConfigDBStringProperty.configdbbaseproperty_ptr'
        db.delete_column('h1ds_configdb_configdbstringproperty', 'configdbbaseproperty_ptr_id')

        # Adding field 'ConfigDBStringProperty.id'
        db.add_column('h1ds_configdb_configdbstringproperty', 'id', self.gf('django.db.models.fields.AutoField')(default=1, primary_key=True), keep_default=False)

        # Deleting field 'ConfigDBFloatProperty.configdbbaseproperty_ptr'
        db.delete_column('h1ds_configdb_configdbfloatproperty', 'configdbbaseproperty_ptr_id')

        # Adding field 'ConfigDBFloatProperty.id'
        db.add_column('h1ds_configdb_configdbfloatproperty', 'id', self.gf('django.db.models.fields.AutoField')(default=1, primary_key=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding model 'ConfigDBBaseProperty'
        db.create_table('h1ds_configdb_configdbbaseproperty', (
            ('configdb_file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['h1ds_configdb.ConfigDBFile'])),
            ('configdb_propertytype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['h1ds_configdb.ConfigDBPropertyType'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('h1ds_configdb', ['ConfigDBBaseProperty'])

        # Deleting model 'ConfigDBProperty'
        db.delete_table('h1ds_configdb_configdbproperty')

        # User chose to not deal with backwards NULL issues for 'ConfigDBIntProperty.configdbbaseproperty_ptr'
        raise RuntimeError("Cannot reverse this migration. 'ConfigDBIntProperty.configdbbaseproperty_ptr' and its values cannot be restored.")

        # Deleting field 'ConfigDBIntProperty.id'
        db.delete_column('h1ds_configdb_configdbintproperty', 'id')

        # Changing field 'ConfigDBIntProperty.value'
        db.alter_column('h1ds_configdb_configdbintproperty', 'value', self.gf('django.db.models.fields.FloatField')())

        # User chose to not deal with backwards NULL issues for 'ConfigDBStringProperty.configdbbaseproperty_ptr'
        raise RuntimeError("Cannot reverse this migration. 'ConfigDBStringProperty.configdbbaseproperty_ptr' and its values cannot be restored.")

        # Deleting field 'ConfigDBStringProperty.id'
        db.delete_column('h1ds_configdb_configdbstringproperty', 'id')

        # User chose to not deal with backwards NULL issues for 'ConfigDBFloatProperty.configdbbaseproperty_ptr'
        raise RuntimeError("Cannot reverse this migration. 'ConfigDBFloatProperty.configdbbaseproperty_ptr' and its values cannot be restored.")

        # Deleting field 'ConfigDBFloatProperty.id'
        db.delete_column('h1ds_configdb_configdbfloatproperty', 'id')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
            'Meta': {'object_name': 'ConfigDBFloatProperty'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        'h1ds_configdb.configdbintproperty': {
            'Meta': {'object_name': 'ConfigDBIntProperty'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'h1ds_configdb.configdbproperty': {
            'Meta': {'object_name': 'ConfigDBProperty'},
            'configdb_file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['h1ds_configdb.ConfigDBFile']"}),
            'configdb_propertytype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['h1ds_configdb.ConfigDBPropertyType']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'h1ds_configdb.configdbpropertytype': {
            'Meta': {'object_name': 'ConfigDBPropertyType'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'h1ds_configdb.configdbstringproperty': {
            'Meta': {'object_name': 'ConfigDBStringProperty'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['h1ds_configdb']
