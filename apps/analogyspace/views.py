from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from csc.conceptnet4.models import Concept
from context import respond_with
import urllib
from commonsense.util import needs_setting, json_view, InputError, ParameterMissingError
from analogyspace.models import YesNoQuestion, Similarity
from csc.corpus.models import get_lang as get_language

def category_from_urlcategory(svd, lang, category):
    parts, concepts, features = unpack_urlcategory(lang, category)
    return make_category_failsoft(svd, concepts, features, parts)

def make_category_failsoft(svd, concepts, features, parts):
    assert len(features) == 0 # FIXME: features currently not supported.
    if len(concepts) == 0:
        raise InputError(u'No concepts given.')
    from csc.conceptnet4.analogyspace import make_category
    try:
        return make_category(svd, concepts, features)
    except KeyError, e:
        concept = e.args[0]
        part = parts[concepts.index(concept)]
        raise InputError(u'Not enough known about "%s" to make a category.' % part)

def unpack_urlcategory(lang, category):
    # Split the category URL into slash-separated parts, and url-decode each.
    parts = [urllib.unquote_plus(part) for part in category.split('/') if part]

    # normalize each part
    def normalize(part):
        try:
            if '/' in part:
                raise InputError('features currently not supported')
            return Concept.get(part, lang).text
        except Concept.DoesNotExist:
            raise InputError(_('Nothing known about the concept "%s".') % part)

    # FIXME: assume they're all concepts for now.
    concepts = [normalize(part) for part in parts]
    features = []
    return parts, concepts, features

def canonical_form(normalized_text, lang):
    # or use canonical_name
    return Concept.objects.get(language=lang, text=normalized_text).text

# Create your views here.
@cache_page(60 * 60)
def similar_concepts_category(request, lang, category):
    # Default to retrieving 10 items.
    count = int(request.GET.get('count', 10))

    svd = get_svd_results(lang)
    cat = category_from_urlcategory(svd, lang, category)
    items = svd.u_dotproducts_with(cat).top_items(count)
    
    concepts = [(canonical_form(text, lang),
                 score) for text, score in items]
    return respond_with('commonsense/_weighted_concepts.html', request,
                        dict(similarities=concepts, lang=lang))

@cache_page(60 * 60)
def similar_concepts(request, lang, concept_name):
    # Default to retrieving 10 items.
    language = get_language(lang)
    count = int(request.GET.get('count', 10))
    try:
        concept = Concept.get(concept_name, language)
    except Concept.DoesNotExist:
        return respond_with('commonsense/concept_noinfo.html', request,
                            {'lang': lang, 'concept_name': concept_name})
    similarities = concept.similarities.values_list('concept2__text', 'score')
    return respond_with('commonsense/_weighted_concepts.html', request,
                        dict(similarities=similarities, lang=lang))

@cache_page(60 * 60)
def predict_features_category(request, lang, category):
    count = int(request.GET.get('count', 5))
    svd = get_svd_results(lang)
    parts, concepts, features = unpack_urlcategory(lang, category)
    cat = make_category_failsoft(svd, concepts, features, parts)
    
    got = 0
    pred_generator = get_predictions_from_vector(lang, concepts, cat, 100)
    predictions = []
    while got < count:
        prediction, score = pred_generator.next()
        predictions.append(prediction)
        got += 1
    return respond_with('commonsense/_predictions.html', request,
                        dict(predictions=predictions, lang=lang))
    
@cache_page(60 * 60)
def predict_features(request, lang, concept_name):
    count = int(request.GET.get('count', 5))
    language = get_language(lang)
    try:
        concept = Concept.get(concept_name, language)
    except Concept.DoesNotExist:
        return respond_with('commonsense/concept_noinfo.html', request,
                            {'lang': lang, 'concept_name': concept_name})
    
    predictions = (
        list(concept.left_ynq.select_related('surface1', 'surface2')[:count]) +
        list(concept.right_ynq.select_related('surface1', 'surface2')[:count])
    )
    predictions = sorted([p for p in predictions if not p.obsolete()])[:count]
    
    return respond_with('commonsense/_predictions.html', request,
                        dict(predictions=predictions, lang=lang))
    
    
    
