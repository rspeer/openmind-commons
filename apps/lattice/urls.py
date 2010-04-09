from django.conf.urls.defaults import *

urlpatterns = patterns(
    'lattice.views',
    url(r'^graph_images/(?P<key>.+)/$', 'serve_cached_image'),
    url(r'^graph/$', 'clientside_map'),
    url(r'^start/(?P<concept_name>.+)/(?P<lr>.+)/(?P<relation_name>.+)/(?P<fconcept_name>.+)/', 'start_lattice'),
)
