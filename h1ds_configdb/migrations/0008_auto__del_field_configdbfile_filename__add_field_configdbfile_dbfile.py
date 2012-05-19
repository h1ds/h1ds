# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'ConfigDBFile.filename'
        db.delete_column('h1ds_configdb_configdbfile', 'filename')

        # Adding field 'ConfigDBFile.dbfile'
        db.add_column('h1ds_configdb_configdbfile', 'dbfile', self.gf('django.db.models.fields.files.FileField')(default='x', max_length=100), keep_default=False)


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'ConfigDBFile.filename'
        raise RuntimeError("Cannot reverse this migration. 'ConfigDBFile.filename' and its values cannot be restored.")

        # Deleting field 'ConfigDBFile.dbfile'
        db.delete_column('h1ds_configdb_configdbfile', 'dbfile')


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
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
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
