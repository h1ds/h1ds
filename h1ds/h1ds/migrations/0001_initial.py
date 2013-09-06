# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Shot'
        db.create_table(u'h1ds_shot', (
            ('number', self.gf('django.db.models.fields.PositiveIntegerField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'h1ds', ['Shot'])

        # Adding model 'Node'
        db.create_table(u'h1ds_node', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shot', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['h1ds.Shot'])),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['h1ds.Node'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('has_data', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('n_dimensions', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('dtype', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('n_channels', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('path_checksum', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'h1ds', ['Node'])

        # Adding model 'FilterDtype'
        db.create_table(u'h1ds_filterdtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('code', self.gf('python_field.fields.PythonCodeField')()),
        ))
        db.send_create_signal(u'h1ds', ['FilterDtype'])

        # Adding model 'FilterDim'
        db.create_table(u'h1ds_filterdim', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('code', self.gf('python_field.fields.PythonCodeField')()),
        ))
        db.send_create_signal(u'h1ds', ['FilterDim'])

        # Adding model 'Filter'
        db.create_table(u'h1ds_filter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('code', self.gf('python_field.fields.PythonCodeField')()),
        ))
        db.send_create_signal(u'h1ds', ['Filter'])

        # Adding M2M table for field data_dim on 'Filter'
        db.create_table(u'h1ds_filter_data_dim', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('filter', models.ForeignKey(orm[u'h1ds.filter'], null=False)),
            ('filterdim', models.ForeignKey(orm[u'h1ds.filterdim'], null=False))
        ))
        db.create_unique(u'h1ds_filter_data_dim', ['filter_id', 'filterdim_id'])

        # Adding M2M table for field data_type on 'Filter'
        db.create_table(u'h1ds_filter_data_type', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('filter', models.ForeignKey(orm[u'h1ds.filter'], null=False)),
            ('filterdtype', models.ForeignKey(orm[u'h1ds.filterdtype'], null=False))
        ))
        db.create_unique(u'h1ds_filter_data_type', ['filter_id', 'filterdtype_id'])

        # Adding model 'H1DSSignal'
        db.create_table(u'h1ds_h1dssignal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal(u'h1ds', ['H1DSSignal'])

        # Adding model 'H1DSSignalInstance'
        db.create_table(u'h1ds_h1dssignalinstance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('signal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['h1ds.H1DSSignal'])),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
        ))
        db.send_create_signal(u'h1ds', ['H1DSSignalInstance'])

        # Adding model 'Pagelet'
        db.create_table(u'h1ds_pagelet', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('pagelet_type', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=2048)),
        ))
        db.send_create_signal(u'h1ds', ['Pagelet'])

        # Adding model 'Worksheet'
        db.create_table(u'h1ds_worksheet', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'h1ds', ['Worksheet'])

        # Adding model 'PageletCoordinates'
        db.create_table(u'h1ds_pageletcoordinates', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pagelet', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['h1ds.Pagelet'])),
            ('worksheet', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['h1ds.Worksheet'])),
            ('coordinates', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'h1ds', ['PageletCoordinates'])

        # Adding model 'UserSignal'
        db.create_table(u'h1ds_usersignal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=2048)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')(blank=True)),
            ('is_fixed_to_shot', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('shot', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'h1ds', ['UserSignal'])


    def backwards(self, orm):
        # Deleting model 'Shot'
        db.delete_table(u'h1ds_shot')

        # Deleting model 'Node'
        db.delete_table(u'h1ds_node')

        # Deleting model 'FilterDtype'
        db.delete_table(u'h1ds_filterdtype')

        # Deleting model 'FilterDim'
        db.delete_table(u'h1ds_filterdim')

        # Deleting model 'Filter'
        db.delete_table(u'h1ds_filter')

        # Removing M2M table for field data_dim on 'Filter'
        db.delete_table('h1ds_filter_data_dim')

        # Removing M2M table for field data_type on 'Filter'
        db.delete_table('h1ds_filter_data_type')

        # Deleting model 'H1DSSignal'
        db.delete_table(u'h1ds_h1dssignal')

        # Deleting model 'H1DSSignalInstance'
        db.delete_table(u'h1ds_h1dssignalinstance')

        # Deleting model 'Pagelet'
        db.delete_table(u'h1ds_pagelet')

        # Deleting model 'Worksheet'
        db.delete_table(u'h1ds_worksheet')

        # Deleting model 'PageletCoordinates'
        db.delete_table(u'h1ds_pageletcoordinates')

        # Deleting model 'UserSignal'
        db.delete_table(u'h1ds_usersignal')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'h1ds.filter': {
            'Meta': {'object_name': 'Filter'},
            'code': ('python_field.fields.PythonCodeField', [], {}),
            'data_dim': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['h1ds.FilterDim']", 'symmetrical': 'False'}),
            'data_type': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['h1ds.FilterDtype']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'h1ds.filterdim': {
            'Meta': {'object_name': 'FilterDim'},
            'code': ('python_field.fields.PythonCodeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'h1ds.filterdtype': {
            'Meta': {'object_name': 'FilterDtype'},
            'code': ('python_field.fields.PythonCodeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'h1ds.h1dssignal': {
            'Meta': {'object_name': 'H1DSSignal'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'h1ds.h1dssignalinstance': {
            'Meta': {'ordering': "('-time',)", 'object_name': 'H1DSSignalInstance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'signal': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['h1ds.H1DSSignal']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'})
        },
        u'h1ds.node': {
            'Meta': {'object_name': 'Node'},
            'dtype': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'has_data': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'n_channels': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'n_dimensions': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['h1ds.Node']"}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'path_checksum': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'shot': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['h1ds.Shot']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'h1ds.pagelet': {
            'Meta': {'object_name': 'Pagelet'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'pagelet_type': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '2048'})
        },
        u'h1ds.pageletcoordinates': {
            'Meta': {'object_name': 'PageletCoordinates'},
            'coordinates': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pagelet': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['h1ds.Pagelet']"}),
            'worksheet': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['h1ds.Worksheet']"})
        },
        u'h1ds.shot': {
            'Meta': {'object_name': 'Shot'},
            'number': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'h1ds.usersignal': {
            'Meta': {'object_name': 'UserSignal'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_fixed_to_shot': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'shot': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '2048'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'h1ds.worksheet': {
            'Meta': {'object_name': 'Worksheet'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'pagelets': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['h1ds.Pagelet']", 'through': u"orm['h1ds.PageletCoordinates']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['h1ds']