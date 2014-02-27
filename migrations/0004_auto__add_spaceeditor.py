# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SpaceEditor'
        db.create_table('spacescout_admin_spaceeditor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('space', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['spacescout_admin.Space'])),
            ('editor', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal('spacescout_admin', ['SpaceEditor'])


    def backwards(self, orm):
        # Deleting model 'SpaceEditor'
        db.delete_table('spacescout_admin_spaceeditor')


    models = {
        'spacescout_admin.space': {
            'Meta': {'object_name': 'Space'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_complete': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'is_pending_publication': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'manager': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'pending': ('django.db.models.fields.TextField', [], {'max_length': '8192', 'null': 'True'}),
            'spot_id': ('django.db.models.fields.SmallIntegerField', [], {'unique': 'True', 'null': 'True'})
        },
        'spacescout_admin.spaceeditor': {
            'Meta': {'object_name': 'SpaceEditor'},
            'editor': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'space': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['spacescout_admin.Space']"})
        },
        'spacescout_admin.spaceimage': {
            'Meta': {'object_name': 'SpaceImage'},
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'display_index': ('django.db.models.fields.SmallIntegerField', [], {}),
            'height': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'space': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['spacescout_admin.Space']"}),
            'upload_application': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'upload_user': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'width': ('django.db.models.fields.IntegerField', [], {})
        },
        'spacescout_admin.spotimagelink': {
            'Meta': {'object_name': 'SpotImageLink'},
            'display_index': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_id': ('django.db.models.fields.SmallIntegerField', [], {'unique': 'True'}),
            'is_deleted': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'space': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['spacescout_admin.Space']"}),
            'spot_id': ('django.db.models.fields.SmallIntegerField', [], {})
        }
    }

    complete_apps = ['spacescout_admin']