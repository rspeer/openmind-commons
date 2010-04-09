from django import template
from settings import MEDIA_URL
from avatar.templatetags.avatar_tags import avatar
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.core.cache import cache
from commonsense.util import cached
from commonsense.queries import *
from django.template.defaultfilters import urlencode
from csc.conceptnet4.models import Proposition
from analogyspace.models import YesNoQuestion
import re, random, cgi

register = template.Library()

@register.simple_tag
def user_link(user):
    avatar_html = avatar(user, size=24)
    url = reverse('profile_detail', args=[user])
    return '<span class="userlink">' + avatar_html + '<a href="'+ url +'">' +\
    user.username + '</a></span>'

@register.filter
def signed_int(n):
    n = int(n)
    if n > 0:
        return mark_safe('<span class="positive">+%s</span>' % n)
    elif n == 0:
        return mark_safe('<span class="zero">%s</span>' % n)
    else:
        return mark_safe('<span class="negative">%s</span>' % n)

def link(target, text):
    return '<a href="%s">%s</a>' % (target, text)

def link_concept_in_assertion(assertion, text):
    return link(reverse('commonsense.views.concept',
                        kwargs={'lang': assertion.language_id,
                                'concept_name': text}),
                text)

@register.simple_tag
def link_concept(concept):
    text = concept.canonical_name
    return link_concept_text(text, concept.language_id)

@register.simple_tag
def link_concept_text(text, lang):
    return link(reverse('commonsense.views.concept',
                        kwargs=dict(lang=lang,
                                    concept_name=text)),
                text)

@register.simple_tag
def list_concepts(concepts):
    return ", ".join(link_concept(c) for c in concepts)

# Helper function needed because the cached decorator changes the function signature.
@cached(lambda assertion: "linked_assertion_"+str(assertion.id), 60*60*24)
def _linked_assertion(assertion):
    return assertion.nl_repr(link_concept_in_assertion)

@register.simple_tag
def linked_assertion(assertion):
    """Hyperlink the concepts in a assertion to their respective pages"""
    return _linked_assertion(assertion)

@register.simple_tag
def with_blanks(frame_text):
    """Replace frame blanks {1}, {2} with input boxes."""
    def input_box(match):
        return '<input type="text" name="field_%d" size="10" />' % int(match.group(1))
    return re.sub(r'\{%\}', '', re.sub(r'\{(\d+)\}', input_box, frame_text))

@register.simple_tag
def with_blanks_filled(frame_text, fill_text, slot):
    """Replace frame blanks {1}, {2} with input boxes."""
    def input_box(match):
        if int(match.group(1)) == slot:
            return '<input type="text" name="field_%d" value="%s" size="10" />' % (int(match.group(1)), fill_text)
        else:
            return '<input type="text" name="field_%d" size="10" />' % int(match.group(1))
    return re.sub(r'\{%\}', '', re.sub(r'\{(\d+)\}', input_box, frame_text))

@register.inclusion_tag('commonsense/_raw_items.html', takes_context=True)
def top_torate(context, lang, num=5):
    return {'raw_assertions': get_top_raw_torate(lang, num),
            'user': context['user']}

# From http://www.djangosnippets.org/snippets/93/
@register.filter
def spaces_and_commas(value, _match_re=re.compile(",(?! )")):
    return _match_re.sub(", ", value)

@register.simple_tag
def vote_arrow(object, objtype, vote, direction):
    id = object.id
    media_url = MEDIA_URL
    if direction == 'up':
        if vote and vote.is_upvote():
            action = 'clearvote'
            icon = 'mod'
        else:
            action = 'upvote'
            icon = 'grey'
    elif direction == 'down':
        if vote and vote.is_downvote():
            action = 'clearvote'
            icon = 'mod'
        else:
            action = 'downvote'
            icon = 'grey'
    return """
    <form class="%(objtype)s_vote" id="%(objtype)s_%(id)s_%(direction)s"
      action="/vote/%(objtype)s/%(id)s/%(action)s/" method="POST">
      <input type="image" id="%(objtype)s_%(id)s_%(direction)s_arrow"
             src="%(media_url)svote/%(direction)s_%(icon)s.png"
             alt="%(direction)s_%(icon)s">
    </form>
    """ % locals()
    
@register.simple_tag
def vote_score(object, objtype, score_obj):
    id = object.id
    if not score_obj or not score_obj.has_key('score'):
        score = 0
    else:
        score = score_obj['score']
    return '<span id="%s_%s_score">%s</span>' % (objtype, id, score)

@register.simple_tag
def format_proposition(prop):
    def emphasize(text):
        return '<b>%s</b>' % text
    if isinstance(prop, Proposition):
        frame, text, slot1, slot2 = prop.nl_parts()
    elif isinstance(prop, YesNoQuestion):
        frame = prop.frame
        slot1 = prop.surface1.text
        slot2 = prop.surface2.text
    else: raise TypeError
    display = frame.fill_in(emphasize(slot1), emphasize(slot2))
    return display

@register.simple_tag
def url_for_feature(feature, lang):
    frame, ftext, text1, text2 = feature.nl_parts('...')
    text1 = urlencode(text1)
    text2 = urlencode(text2)
    return "/%s/add_statement/%s/%s/%s/" % (lang, frame.id, text1, text2)

@register.simple_tag
def answer_url(prop, value):
    if isinstance(prop, Proposition):
        frame, text, slot1, slot2 = prop.nl_parts()
    elif isinstance(prop, YesNoQuestion):
        frame = prop.frame
        slot1 = prop.surface1.text
        slot2 = prop.surface2.text
    text1 = urlencode(slot1)
    text2 = urlencode(slot2)
    lang = frame.language.id
    if value == 'yes':
        return "/%s/add_statement/%s/%s/%s/?context=yes" % (lang, frame.id, text1, text2)
    elif value == 'no':
        return "/%s/submit_statement/?frame_id=%s&text1=%s&text2=%s&vote=-1&activity=commons2_reject" % (lang, frame.id, text1, text2)
    elif value == 'maybe':
        return "/%s/add_statement/%s/%s/%s/?context=maybe" % (lang, frame.id, text1, text2)
    else: raise ValueError

@register.simple_tag
def statement_form(frame, text1, text2):
    input1 = '<input type="text" width=15 name="text1" value="%s" />' % cgi.escape(text1, True)
    input2 = '<input type="text" width=15 name="text2" value="%s" />' % cgi.escape(text2, True)
    framehtml = frame.fill_in(input1, input2)
    return framehtml
statement_form.is_safe = True
