# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.views.generic.list_detail import object_list
from csc.conceptnet.models import Assertion, RawAssertion, Frame,\
Relation, Concept, Language, Sentence
from csc.corpus.models import get_lang as get_language
from commonsense.queries import get_top_raw_torate, get_random_concepts,\
add_assertion, get_recent_raw
from voting.models import Vote
from voting.views import vote_on_object, VOTE_DIRECTIONS
from events.models import Event, Activity
from django.core.paginator import Paginator

from commonsense.util import needs_setting, json_view, InputError, ParameterMissingError
from context import respond_with

def main_page(request):
    languages = []
    for language in Language.objects.all():
        if language.id == 'zh-Hans':
            # not ready for simp. Chinese yet
            continue
        count = language.sentence_count
        if count > 1:
            languages.append((language.id, language.name, count))
    languages.sort(key = lambda x: -x[2])
    lang = 'en' # FIXME
    return respond_with('commonsense/main.html', request, {'languages':
    languages, 'lang': lang})

def concept(request, lang, concept_name):
    '''View for displaying a concept, specified by text.'''
    language = get_language(lang)
    try:
        concept = Concept.get(concept_name, language)
    except Concept.DoesNotExist:
        return respond_with('commonsense/concept_noinfo.html', request,
                            {'lang': lang, 'concept_name': concept_name})

    queryset = concept.raw_assertions_no_dupes().select_related('surface1', 'surface2', 'frame')
    return respond_with('commonsense/concept.html', request, dict(
        concept_name=concept_name,
        concept=concept,
        lang=lang,
        user=request.user,
        language=language,
        raw_assertions=queryset
    ))

def feature(request, lang, lr, relation_name, concept_name):
    language = get_language(lang)
    concept = Concept.objects.get(concept_name, language)
    relation = Relation.get(relation_name)
    cls = {'left': LeftFeature, 'right': RightFeature}[lr]
    feature = cls(relation, concept)
    return respond_with('commonsense/feature.html', request, dict(
            feature = feature))

def assertion(request, lang, assertion_id):
    language = get_language(lang)
    the_assertion = get_object_or_404(Assertion.objects, pk=int(assertion_id))
    raw_assertions = the_assertion.rawassertion_set.order_by('-score')
    raw_assertions = raw_assertions.select_related('surface1', 'surface2', 'frame', 'frequency')
    
    if request.user:
        vote = Vote.objects.get_for_user(the_assertion, request.user)
        if vote:
            if (len(raw_assertions) == 1 and raw_assertions[0].creator ==
            request.user):
                if vote.is_upvote():
                    request.user.message_set.create(message=ugettext("""
                        Thanks for contributing! Here is the assertion you
                        created.
                    """))
                elif vote.is_downvote():
                    request.user.message_set.create(message=ugettext("""
                        Thanks for contributing! You disagreed with this
                        prediction, helping Open Mind make better predictions
                        in the future.
                    """))

            else:
                if vote.is_upvote():
                    request.user.message_set.create(message=ugettext("""
                      You have voted for this assertion. We encourage you to also
                      vote on the statements that support the assertion, below.
                      Vote for the ones that you think are the best way to say it.
                    """))
                elif vote.is_downvote():
                    request.user.message_set.create(message=ugettext("""
                      You have voted against this assertion. We encourage you to also
                      vote on the statements that support the assertion, below.
                      Unless they were simply misunderstood by Open Mind, you may
                      want to vote against them as well.
                    """))
    raw_assertions = raw_assertions.filter(score__gt=-1)
    return respond_with('commonsense/assertion.html', request, locals())

def concept_overview(request, lang):
    if 'concept_name' in request.POST:
        return concept(request, lang, request.POST['concept_name'])
    language = get_language(lang)
    concepts = get_random_concepts(language, 10)
    return respond_with('commonsense/concept_overview.html', request, locals())

def random_statements(request, lang, offset=0):
    offset = int(offset)
    language = get_language(lang)
    raw_assertions = get_top_raw_torate(language, 15, offset)
    next = offset+1
    return respond_with('commonsense/statement_overview.html', request, locals())

def recent_statements(request, lang, offset=0):
    offset = int(offset)
    language = get_language(lang)
    raw_assertions = get_recent_raw(language, 15, offset)
    next = offset+1
    return respond_with('commonsense/statement_recent.html', request, locals())

def statement_overview(request, lang, offset=0):
    offset = int(offset)
    language = get_language(lang)
    raw_assertions = get_top_raw_torate(language, 15, min_assertion_score=2,
                                        offset=offset)
    next = offset+1
    return respond_with('commonsense/statement_overview.html', request, locals())

def add_message(request, text):
    request.user.message_set.create(message=ugettext(text))

def add_statement(request, lang, frame_id, text1, text2):
    frame = get_object_or_404(Frame.objects, pk=int(frame_id))
    if text1 in ('-', '...'): text1 = ''
    if text2 in ('-', '...'): text2 = ''
    field1 = '<input type="text" name="text1" value="%s">' % text1
    field2 = '<input type="text" name="text2" value="%s">' % text2
    if 'context' in request.GET:
        if request.GET['context'] == 'yes':
            add_message(request, """
                You said that this is true. You can now change the grammar or
                wording of the statement if you want. Click Add to teach this
                new fact to Open Mind.
            """)
        elif request.GET['context'] == 'maybe':
            add_message(request, """
                You said that this is sort of true. Can you change the text to
                make a statement that you consider true?
            """)
    possible_frames = Frame.objects.filter(language=frame.language,
      relation=frame.relation, goodness__gte=3)
    #show_frames = len(possible_frames) > 1
    show_frames = False
            
    return respond_with('commonsense/add_statement.html', request, locals())

def add_main(request, lang):
    relations = Relation.objects.filter(description__isnull=False)
    suggestions = []
    for r in relations:
        frames = Frame.objects.filter(relation=r, language__id=lang,
        goodness__gte=2).order_by('-goodness')
        if len(frames) == 0: continue
        if r.description.startswith('*'): continue
        suggestions.append((r, frames[0]))
    return respond_with('commonsense/add_main.html', request, locals())

@login_required
def add_from_frame(request, lang):
    try:
        if not 'frame_id' in request.REQUEST: raise ParameterMissingError('frame_id')
        frame = Frame.objects.get(id=int(request.REQUEST['frame_id']))
    except Exception:
        raise
        #raise InputError('Frame not found.')

    try:
        text1 = request.REQUEST['text1']
        text2 = request.REQUEST['text2']
        vote = int(request.REQUEST['vote'])
        activity_name = request.REQUEST['activity']
        if len(text1) == 0 or len(text2) == 0:
            raise InputError('One of the slots was not filled in.')
    except KeyError, e:
        raise ParameterMissingError(e)

    user = request.user
    activity, created = Activity.objects.get_or_create(name=activity_name)
    if created: activity.save()
    the_assertion = add_assertion(request, user, frame, text1, text2, activity,
    vote)
    return assertion(request, lang, the_assertion.id)

@login_required
def vote_on_statement(request, object_id, direction):
    raw = RawAssertion.objects.get(id=object_id)
    vote = dict(VOTE_DIRECTIONS)[direction]
    response = vote_on_object(request, object_id=object_id, direction=direction,
                              model=RawAssertion, template_object_name='statement',
                              allow_xmlhttprequest=True)
    if not Vote.objects.get_for_user(raw.assertion, request.user):
        Vote.objects.record_vote(raw.assertion, request.user, vote)
        raw.assertion.update_score()
    raw.update_score()
    return response

@login_required
def vote_on_assertion(request, object_id, direction):
    assertion = Assertion.objects.get(id=object_id)
    vote = dict(VOTE_DIRECTIONS)[direction]
    response = vote_on_object(request, object_id=object_id, direction=direction,
                              model=Assertion, template_object_name='assertion',
                              allow_xmlhttprequest=True)
    assertion.update_score()
    return response

