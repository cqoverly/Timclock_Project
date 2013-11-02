# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'TimestampEdits.timestampID'
        db.delete_column(u'app_timeclock_timestampedits', 'timestampID_id')

        # Adding field 'TimestampEdits.timestamp'
        db.add_column(u'app_timeclock_timestampedits', 'timestamp',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['app_timeclock.Timestamp']),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'TimestampEdits.timestampID'
        db.add_column(u'app_timeclock_timestampedits', 'timestampID',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['app_timeclock.Timestamp']),
                      keep_default=False)

        # Deleting field 'TimestampEdits.timestamp'
        db.delete_column(u'app_timeclock_timestampedits', 'timestamp_id')


    models = {
        u'app_timeclock.timestamp': {
            'Meta': {'object_name': 'Timestamp'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_out': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'stamp': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'app_timeclock.timestampedits': {
            'Meta': {'object_name': 'TimestampEdits'},
            'change_reason': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_changed_by'", 'to': u"orm['auth.User']"}),
            'date_changed': ('django.db.models.fields.DateTimeField', [], {}),
            'for_employee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_for_employee'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'new_inout': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'original_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'original_inout': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'timestamp': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_timeclock.Timestamp']"})
        },
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
        }
    }

    complete_apps = ['app_timeclock']