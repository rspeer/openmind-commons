from django.db import models
from analogyspace.analysis import predictions_for_concept,\
  similarities_for_concept, all_svd_concepts
from csc.conceptnet4.models import Frame, Concept, Relation, TimestampedModel,\
  SurfaceForm, Assertion
from csc.corpus.models import Language
from decimal import Decimal

def makeDecimal(f):
    return Decimal(str(f))

def make_predictions(lang):
    YesNoQuestion.objects.update_all(lang)
    Similarity.objects.update_all(lang)

class PredictionCacheManager(models.Manager):
    def update_all(self, lang='en', n=10):
        if isinstance(lang, Language): lang = lang.id
        for conceptname in all_svd_concepts(lang):
            concept = Concept.get_raw(conceptname, lang)
            print concept
            self.update_concept(concept, n)
            
    def update_oldest(self):
        oldest = self.all().order_by('updated')[0]
        self.update_concept(oldest)

class YesNoManager(PredictionCacheManager):
    def prune_concept(self, concept, n=10):
        for qset in (concept.left_ynq, concept.right_ynq):
            obsolete = qset.all()[n:]
            for ynq in obsolete:
                ynq.delete()
    
    def update_concept(self, concept, n=10):
        for prop, score in predictions_for_concept(concept.language.id,
                                                   concept.text, n):
            frame, ftext, surface1, surface2 = prop.nl_parts()
            surface1 = SurfaceForm.get(surface1, concept.language)
            surface2 = SurfaceForm.get(surface2, concept.language)
            
            ynq, created = self.get_or_create(
                relation=frame.relation, concept1=surface1.concept,
                concept2=surface2.concept,
                defaults=dict(
                    frame=frame, surface1=surface1, surface2=surface2,
                )
            )
            ynq.score = makeDecimal(score)
            ynq.surface1 = surface1
            ynq.surface2 = surface2
            ynq.frame = frame
            ynq.save()
        self.prune_concept(concept, n)

class YesNoQuestion(TimestampedModel):
    frame = models.ForeignKey(Frame)
    surface1 = models.ForeignKey(SurfaceForm, related_name='left_ynq')
    surface2 = models.ForeignKey(SurfaceForm, related_name='right_ynq')
    relation = models.ForeignKey(Relation)
    concept1 = models.ForeignKey(Concept, related_name='left_ynq')
    concept2 = models.ForeignKey(Concept, related_name='right_ynq')
    score = models.DecimalField(default=Decimal('0'), max_digits=16,
                                decimal_places=6)
    
    objects = YesNoManager()

    def __unicode__(self):
        return "%s [%s]" % (self.frame.fill_in(self.surface1.text,
        self.surface2.text), self.score)
    
    def obsolete(self):
        return (Assertion.objects.filter(concept1=self.concept1,
                                         concept2=self.concept2,
                                         relation=self.relation).count() > 0)
    
    class Meta:
        ordering = ['-score']

class SimilarityManager(PredictionCacheManager):
    def prune_concept(self, concept, n=10):
        obsolete = concept.similarities.all()[n:]
        for sim in obsolete:
            sim.delete()
    
    def update_concept(self, concept, n=10):
        for target, score in similarities_for_concept(concept.language.id,
                                                      concept.text, n):
            sim, created = self.get_or_create(
                concept1=concept, concept2=Concept.get_raw(target, concept.language.id)
            )
            sim.score = makeDecimal(score)
            sim.save()
        self.prune_concept(concept)
            
class Similarity(TimestampedModel):
    concept1 = models.ForeignKey(Concept, related_name='similarities')
    concept2 = models.ForeignKey(Concept, related_name='incoming_similarities')
    score = models.DecimalField(default=Decimal('0'), max_digits=16,
                                decimal_places=6)
    
    objects = SimilarityManager()
    
    def __unicode__(self):
        return "%s ~ %s [%s]" % (self.concept1, self.concept2, self.score)

    class Meta:
        ordering = ['-score']
        