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

import urllib

@json_view
def username_available(request):
    return {'exists': _user_exists(request.GET['username'])}

def add_from_frame(request):
    if 'username' in request.POST:
        from django.contrib.auth import authenticate, login
        user = authenticate(username=request.POST['username'],
                            password=request.POST['password'])
        if user is not None and user.is_active:
            login(request, user)
        else:
            raise InputError(_('Login failed'))

    return add_from_frame_real(request)

@login_required
@json_view
def add_from_frame_real(request):
    # FIXME FIXME FIXME
    try:
        if not 'frame_id' in request.POST: raise ParameterMissingError('frame_id')
        frame = Frame.objects.get(id=int(request.POST['frame_id']))
    except Exception:
        raise InputError(_('Frame not found.'))

    try:
        text1 = request.POST['text1']
        text2 = request.POST['text2']
        if len(text1) == 0 or len(text2) == 0:
            raise InputError(_('One of the slots was not filled in.'))
        activity_name = request.POST['activity']
        rating = get_rating_value(request.POST.get('rating', 'Good'))
    except KeyError, e:
        raise ParameterMissingError(e)

    user = request.user
    activity, created = Activity.objects.get_or_create(name=activity_name)
    add_assertion(request, user, frame, text1, text2, activity, rating)

    return {'text': _('Knowledge accepted.')}

def concept_fwd(request, lang, concept):
    return _concept_relations(request, lang, concept, 'fwd')
def concept_rev(request, lang, concept):
    return _concept_relations(request, lang, concept, 'rev')
def concept_all_relations(request, lang, concept):
    return _concept_relations(request, lang, concept, 'all')


@json_view
def _concept_relations(request, lang, concept, filter='all'):
    types = request.GET.get('types', 'All')
    limit = int(request.GET.get('limit', 10))
    concept_obj = Concept.get(concept, lang)
    if filter == 'all':
        assertions = concept_obj.get_assertions(useful_only=True)
    elif filter == 'fwd':
        assertions = concept_obj.right_assertion_set.all()
    elif filter == 'rev':
        assertions = concept_obj.left_assertion_set.all()
    else:
        raise TypeError('unknown concept_relations filter: %s' % (filter,))

    if types != 'All':
        relations = [Relation.objects.get(name=t) for t in types.split(',')]
        import operator
        filters = reduce(operator.or_, [Q(relation=rel) for rel in relations])
        assertions = assertions.filter(filters)

    return {'assertions': [assertion_to_dict(a) for a in assertions[:limit]]}


def concept_to_dict(c):
    return dict(
        id=c.id,
        language=c.language_id,
        normalized=c.text,
        num_assertions=c.num_predicates,
        canonical_name=c.canonical_name)

def assertion_to_dict(a):
    return dict(id=a.id, left=concept_to_dict(a.concept1),
                type=a.relation.name, right=concept_to_dict(a.concept2),
                score=a.score, sentence=a.nl_repr())

@json_view
def assertion_info(request, lang, id):
    return assertion_to_dict(get_object_or_404(Assertion, id=id, language=lang))

@json_view
def concept_info(request, lang, concept):
    return concept_to_dict(Concept.get(concept, lang))
