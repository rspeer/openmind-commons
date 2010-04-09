from django.conf.urls.defaults import *

urlpatterns = patterns(
    'analogyspace.views',
    # (r'^similar_concepts/(?P<category>.*)/$', 'similar_concepts'),
    # (r'^predict_features/(?P<category>.*)/$', 'predict_features'),
    (r'^(?P<lang>.+)/similar_concepts/(?P<concept_name>.*)/$', 'similar_concepts'),
    (r'^(?P<lang>.+)/predict_features/(?P<concept_name>.*)/$', 'predict_features'),
)

