
from south.db import db
from django.db import models
from analogyspace.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Similarity'
        db.create_table('analogyspace_similarity', (
            ('id', orm['analogyspace.Similarity:id']),
            ('created', orm['analogyspace.Similarity:created']),
            ('updated', orm['analogyspace.Similarity:updated']),
            ('concept1', orm['analogyspace.Similarity:concept1']),
            ('concept2', orm['analogyspace.Similarity:concept2']),
            ('score', orm['analogyspace.Similarity:score']),
        ))
        db.send_create_signal('analogyspace', ['Similarity'])
        
        # Adding model 'YesNoQuestion'
        db.create_table('analogyspace_yesnoquestion', (
            ('id', orm['analogyspace.YesNoQuestion:id']),
            ('created', orm['analogyspace.YesNoQuestion:created']),
            ('updated', orm['analogyspace.YesNoQuestion:updated']),
            ('frame', orm['analogyspace.YesNoQuestion:frame']),
            ('surface1', orm['analogyspace.YesNoQuestion:surface1']),
            ('surface2', orm['analogyspace.YesNoQuestion:surface2']),
            ('relation', orm['analogyspace.YesNoQuestion:relation']),
            ('concept1', orm['analogyspace.YesNoQuestion:concept1']),
            ('concept2', orm['analogyspace.YesNoQuestion:concept2']),
            ('score', orm['analogyspace.YesNoQuestion:score']),
        ))
        db.send_create_signal('analogyspace', ['YesNoQuestion'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Similarity'
        db.delete_table('analogyspace_similarity')
        
        # Deleting model 'YesNoQuestion'
        db.delete_table('analogyspace_yesnoquestion')
        
    
    
    models = {
        'analogyspace.similarity': {
            'concept1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'similarities'", 'to': "orm['conceptnet4.Concept']"}),
            'concept2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'incoming_similarities'", 'to': "orm['conceptnet4.Concept']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.DecimalField', [], {'default': 'Decimal("0")', 'max_digits': '16', 'decimal_places': '6'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {})
        },
        'analogyspace.yesnoquestion': {
            'concept1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'left_ynq'", 'to': "orm['conceptnet4.Concept']"}),
            'concept2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'right_ynq'", 'to': "orm['conceptnet4.Concept']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'frame': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['conceptnet4.Frame']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'relation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['conceptnet4.Relation']"}),
            'score': ('django.db.models.fields.DecimalField', [], {'default': 'Decimal("0")', 'max_digits': '16', 'decimal_places': '6'}),
            'surface1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'left_ynq'", 'to': "orm['conceptnet4.SurfaceForm']"}),
            'surface2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'right_ynq'", 'to': "orm['conceptnet4.SurfaceForm']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {})
        },
        'conceptnet4.concept': {
            'Meta': {'unique_together': "(('language', 'text'),)", 'db_table': "'concepts'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corpus.Language']"}),
            'num_assertions': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'text': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'words': ('django.db.models.fields.IntegerField', [], {})
        },
        'conceptnet4.frame': {
            'Meta': {'db_table': "'conceptnet_frames'"},
            'frequency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nl.Frequency']"}),
            'goodness': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corpus.Language']"}),
            'question1': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'question2': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'question_yn': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'relation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['conceptnet4.Relation']"}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'conceptnet4.relation': {
            'Meta': {'db_table': "'predicatetypes'"},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'conceptnet4.surfaceform': {
            'Meta': {'unique_together': "(('language', 'text'),)", 'db_table': "'surface_forms'"},
            'concept': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['conceptnet4.Concept']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corpus.Language']"}),
            'residue': ('django.db.models.fields.TextField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'use_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'corpus.language': {
            'id': ('django.db.models.fields.CharField', [], {'max_length': '16', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'sentence_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'nl.frequency': {
            'Meta': {'unique_together': "(('language', 'text'),)", 'db_table': "'conceptnet_frequency'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corpus.Language']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        }
    }
    
    complete_apps = ['analogyspace']
