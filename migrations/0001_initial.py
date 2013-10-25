# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Space'
        db.create_table('spacescout_admin_space', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('spot_id', self.gf('django.db.models.fields.SmallIntegerField')(unique=True, null=True)),
            ('is_complete', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('manager', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('modified_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('pending', self.gf('django.db.models.fields.TextField')(max_length=8192, null=True)),
        ))
        db.send_create_signal('spacescout_admin', ['Space'])

        # Adding model 'SpaceImage'
        db.create_table('spacescout_admin_spaceimage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('space', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['spacescout_admin.Space'])),
            ('content_type', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('width', self.gf('django.db.models.fields.IntegerField')()),
            ('height', self.gf('django.db.models.fields.IntegerField')()),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modification_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('upload_user', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('upload_application', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('spacescout_admin', ['SpaceImage'])


    def backwards(self, orm):
        # Deleting model 'Space'
        db.delete_table('spacescout_admin_space')

        # Deleting model 'SpaceImage'
        db.delete_table('spacescout_admin_spaceimage')


    models = {
        'spacescout_admin.space': {
            'Meta': {'object_name': 'Space'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_complete': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'manager': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'pending': ('django.db.models.fields.TextField', [], {'max_length': '8192', 'null': 'True'}),
            'spot_id': ('django.db.models.fields.SmallIntegerField', [], {'unique': 'True', 'null': 'True'})
        },
        'spacescout_admin.spaceimage': {
            'Meta': {'object_name': 'SpaceImage'},
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'space': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['spacescout_admin.Space']"}),
            'upload_application': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'upload_user': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'width': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['spacescout_admin']