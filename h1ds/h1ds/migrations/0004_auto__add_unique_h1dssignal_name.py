# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding unique constraint on 'H1DSSignal', fields ['name']
        db.create_unique('h1ds_core_h1dssignal', ['name'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'H1DSSignal', fields ['name']
        db.delete_unique('h1ds_core_h1dssignal', ['name'])


    models = {
        'h1ds_core.h1dssignal': {
            'Meta': {'object_name': 'H1DSSignal'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'h1ds_core.h1dssignalinstance': {
            'Meta': {'ordering': "('-time',)", 'object_name': 'H1DSSignalInstance'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'signal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['h1ds_core.H1DSSignal']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['h1ds_core']
