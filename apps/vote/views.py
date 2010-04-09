# Create your views here.
from django.contrib.auth.decorators import login_required
from csc.conceptnet.models import Assertion, RawAssertion, Frame,\
Relation, Concept, Language, Sentence
from voting.models import Vote
from voting.views import vote_on_object, VOTE_DIRECTIONS

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


