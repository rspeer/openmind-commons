from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
import re

from events.models import Activity
from csc.conceptnet4.models import Assertion, Frame, Concept, Relation, Feature

from commonsense.util import needs_setting, json_view, InputError, ParameterMissingError
from commonsense.queries import _user_exists, add_assertion, get_top_torate
from analogyspace.analysis import get_svd_results, tensor_filename, get_tensor

import urllib


def canonical_form(normalized_text, lang):
    return Concept.objects.get(language=lang, text=normalized_text).canonical_name

@cache_page(60 * 60)
@json_view
def similar_concepts(request, lang, category):
    # Default to retrieving 10 items.
    count = int(request.GET.get('count', 10))

    svd = get_svd_results(lang)
    cat = category_from_urlcategory(svd, lang, category)
    items = svd.u_distances_to(cat).top_items(count)

    return {
        'similar':
            [{
                'text': canonical_form(item[0], lang),
                'score': item[1],
                } for item in items]
        }


@json_view
def similar_features(request, lang, category):
    # Default to retrieving 10 items.
    count = int(request.GET.get('count', 10))
    fmt = request.GET.get('format', 'frame_blank')

    svd = get_svd_results(lang)
    cat = category_from_urlcategory(svd, lang, category)
    items = svd.v_distances_to(cat).top_items(count)

    def feature_to_dict(feature_tup, score):
        feature = Feature.from_tuple(feature_tup)
        return dict(
            raw = feature_tup,
            logical = str(feature),
            text = feature.nl_statement('__'),
            score = score
            )

    return {
        'similar':
            [feature_to_dict(feature, score) for (feature, score) in items]
        }

@json_view
def eval_assertion(request, lang, concept1, reltype, concept2):
    c1 = Concept.get(concept1, lang)
    c2 = Concept.get(concept2, lang)

    svd = get_svd_results(lang)

    from csc.conceptnet4.analogyspace import eval_assertion
    lval, rval = eval_assertion(svd, relationtype=reltype, ltext=c1.text, rtext=c2.text)

    return {'lfeat_val': lval,
            'rfeat_val': rval}

def get_predictions(lang, concepts):
    count = 100
    tensor = get_tensor(lang)
    svd = get_svd_results(lang)
    cat = make_category_failsoft(svd, concepts, [], concepts)
    return get_prediction_vector(lang, cat)

def iterlim(iter, lim):
    count = 0
    while count < lim:
        yield iter.next()
        count += 1

@json_view
def predicted(request, lang, category):
    limit = int(request.GET.get('limit', 3))
    parts, concepts, features = unpack_urlcategory(lang, category)
    predictions = get_predictions(lang, concepts)
    predictions_parts = (prop.nl_parts() + (score,) for prop, score in iterlim(predictions, limit))

    return {
        'predictions':
            [dict(left=surface1, frame=frame.text, right=surface2, reltype=frame.relation.name,
                  score=score, frame_id=frame.id)
             for frame, frame_text, surface1, surface2, score in predictions_parts]
        }

def tensor_download(request, lang):
    return HttpResponse(open(tensor_filename(lang), 'rb'), mimetype='application/x-gzip')


@json_view
def category_similarity(request, lang, cat1, cat2):
    from math import sqrt

    svd = get_svd_results(lang)
    cat1_vec = category_from_urlcategory(svd, lang, cat1)
    cat2_vec = category_from_urlcategory(svd, lang, cat2)

    return {
        'similarity':
            cat1_vec*cat2_vec / (sqrt(cat1_vec*cat1_vec) * sqrt(cat2_vec*cat2_vec))
        }
