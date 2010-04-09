from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('usertest.views',
    url(r'^$', direct_to_template, {"template": "usertest/start.html"}),
    url(r'^questions/$', 'ask_questions'),
    url(r'^answers/$', 'get_answers'),
)

