# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Renaming column for 'H1DSSignalInstance.signal' to match new field type.
        db.rename_column('h1ds_core_h1dssignalinstance', 'signal', 'signal_id')
        # Changing field 'H1DSSignalInstance.signal'
        db.alter_column('h1ds_core_h1dssignalinstance', 'signal_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['h1ds_core.H1DSSignal']))

        # Adding index on 'H1DSSignalInstance', fields ['signal']
        db.create_index('h1ds_core_h1dssignalinstance', ['signal_id'])


    def backwards(self, orm):
        
        # Removing index on 'H1DSSignalInstance', fields ['signal']
        db.delete_index('h1ds_core_h1dssignalinstance', ['signal_id'])

        # Renaming column for 'H1DSSignalInstance.signal' to match new field type.
        db.rename_column('h1ds_core_h1dssignalinstance', 'signal_id', 'signal')
        # Changing field 'H1DSSignalInstance.signal'
        db.alter_column('h1ds_core_h1dssignalinstance', 'signal', self.gf('django.db.models.fields.CharField')(max_length=50))


    models = {
        'h1ds_core.h1dssignal': {
            'Meta': {'object_name': 'H1DSSignal'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'h1ds_core.h1dssignalinstance': {
            'Meta': {'ordering': "('-time',)", 'object_name': 'H1DSSignalInstance'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'signal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['h1ds_core.H1DSSignal']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['h1ds_core']
