from django.conf.urls.defaults import *

urlpatterns = []

urlpatterns += patterns(
    'commonsense.views',
    url(r'^$', 'concept_overview', name='concepts'),
    url(r'^concept/$', 'concept_overview', name='concepts'),
    url(r'^statement/$', 'statement_overview', name='statements'),
    url(r'^statement/(?P<offset>\d+)$', 'statement_overview',
        name='statements_n'),
    url(r'^statement/recent/$', 'recent_statements', name='statements_recent'),
    url(r'^statement/recent/(?P<offset>\d+)$', 'recent_statements',
        name='statements_recent_n'),
    url(r'^statement/random/$', 'random_statements', name='statements_random'),
    url(r'^statement/random/(?P<offset>\d+)$', 'random_statements',
        name='statements_random_n'),
    #url(r'^knowledge/recent/$', 'recent', name='recent'),
    #url(r'^knowledge/top/$', 'top_knowledge', name='top_knowledge'),
    url(r'^concept/(?P<concept_name>.*)/$', 'concept', name='concept'),
    url(r'^assertion/(?P<assertion_id>.*)/$', 'assertion', name='assertion'),
    url(r'^add/', 'add_main', name='add_main'),
    url(r'^add_statement/(?P<frame_id>.*)/(?P<text1>.*)/(?P<text2>.*)/$', 'add_statement', name='add_statement'),
    url(r'^submit_statement/$', 'add_from_frame', name='submit_statement'),
)

