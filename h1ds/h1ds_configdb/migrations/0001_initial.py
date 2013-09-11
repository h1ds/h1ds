# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ConfigDBLoadingDir'
        db.create_table(u'h1ds_configdb_configdbloadingdir', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('folder', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('force_overwrite', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'h1ds_configdb', ['ConfigDBLoadingDir'])

        # Adding model 'ConfigDBFileType'
        db.create_table(u'h1ds_configdb_configdbfiletype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('mimetype', self.gf('django.db.models.fields.CharField')(max_length=126)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
        ))
        db.send_create_signal(u'h1ds_configdb', ['ConfigDBFileType'])

        # Adding model 'ConfigDBPropertyType'
        db.create_table(u'h1ds_configdb_configdbpropertytype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('value_type', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal(u'h1ds_configdb', ['ConfigDBPropertyType'])

        # Adding model 'ConfigDBProperty'
        db.create_table(u'h1ds_configdb_configdbproperty', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('configdb_file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['h1ds_configdb.ConfigDBFile'])),
            ('configdb_propertytype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['h1ds_configdb.ConfigDBPropertyType'])),
            ('value_float', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('value_integer', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('value_string', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal(u'h1ds_configdb', ['ConfigDBProperty'])

        # Adding model 'ConfigDBFile'
        db.create_table(u'h1ds_configdb_configdbfile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dbfile', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('filetype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['h1ds_configdb.ConfigDBFileType'])),
            ('md5sum', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal(u'h1ds_configdb', ['ConfigDBFile'])


    def backwards(self, orm):
        # Deleting model 'ConfigDBLoadingDir'
        db.delete_table(u'h1ds_configdb_configdbloadingdir')

        # Deleting model 'ConfigDBFileType'
        db.delete_table(u'h1ds_configdb_configdbfiletype')

        # Deleting model 'ConfigDBPropertyType'
        db.delete_table(u'h1ds_configdb_configdbpropertytype')

        # Deleting model 'ConfigDBProperty'
        db.delete_table(u'h1ds_configdb_configdbproperty')

        # Deleting model 'ConfigDBFile'
        db.delete_table(u'h1ds_configdb_configdbfile')


    models = {
        u'h1ds_configdb.configdbfile': {
            'Meta': {'object_name': 'ConfigDBFile'},
            'dbfile': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'filetype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['h1ds_configdb.ConfigDBFileType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'md5sum': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'h1ds_configdb.configdbfiletype': {
            'Meta': {'object_name': 'ConfigDBFileType'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '126'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'h1ds_configdb.configdbloadingdir': {
            'Meta': {'object_name': 'ConfigDBLoadingDir'},
            'folder': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'force_overwrite': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'h1ds_configdb.configdbproperty': {
            'Meta': {'object_name': 'ConfigDBProperty'},
            'configdb_file': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['h1ds_configdb.ConfigDBFile']"}),
            'configdb_propertytype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['h1ds_configdb.ConfigDBPropertyType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value_float': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'value_integer': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'value_string': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        u'h1ds_configdb.configdbpropertytype': {
            'Meta': {'object_name': 'ConfigDBPropertyType'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'value_type': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        }
    }

    complete_apps = ['h1ds_configdb']