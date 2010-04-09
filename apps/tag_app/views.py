from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

# Modified for Open Mind
from csc.conceptnet4.models import Assertion, RawAssertion, User
from tagging.models import Tag, TaggedItem

def tags(request, tag, template_name='tags/index.html'):
    tag = get_object_or_404(Tag, name=tag)
    
    assertion_tags = TaggedItem.objects.get_by_model(Assertion,
    tag).filter(score__gt=0)
    
    raw_tags = RawAssertion.objects.get_by_model(RawAssertion,
    tag).filter(score__gt=0)

    user_tags = RawAssertion.objects.get_by_model(User, tag)

    return render_to_response(template_name, locals(),
    context_instance=RequestContext(request))

