from django.conf.urls.defaults import *

urlpatterns = patterns(
    'vote.views',
    (r'statement/(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/?$', 'vote_on_statement'),
    (r'assertion/(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/?$', 'vote_on_assertion'),
)

