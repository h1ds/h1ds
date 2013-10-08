# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'SummaryAttribute.device'
        default_device_pk = orm['h1ds.Device'].objects.get(is_default=True).pk
        db.add_column(u'h1ds_summary_summaryattribute', 'device',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=default_device_pk, to=orm['h1ds.Device'], on_delete=models.PROTECT),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'SummaryAttribute.device'
        db.delete_column(u'h1ds_summary_summaryattribute', 'device_id')

    models = {
        u'h1ds.device': {
            'Meta': {'object_name': 'Device'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'latest_shot': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['h1ds.Shot']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'h1ds.shot': {
            'Meta': {'object_name': 'Shot'},
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['h1ds.Device']", 'on_delete': 'models.PROTECT'}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'h1ds_summary.summaryattribute': {
            'Meta': {'ordering': "['display_order', 'slug']", 'object_name': 'SummaryAttribute'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['h1ds.Device']", 'on_delete': 'models.PROTECT'}),
            'display_order': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'format_string': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['h1ds_summary']