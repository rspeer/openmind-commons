#-*- coding: utf-8 -*-
from pinax_settings import *
TENSOR_ROOT = PROJECT_ROOT + '/tensors/'
SVD_LANGUAGES = ['en', 'ja', 'zh']

MIDDLEWARE_CLASSES += (
    'middleware.LanguageOverrideMiddleware',
)

INSTALLED_APPS += (
    'django.contrib.admin',
    'commonsense',
    'analogyspace',
    'colorizer',
    'usertest',
    'csc.conceptnet',
    'csc.corpus',
    'csc.webapi',
    'south',
    'rosetta',
    'voting',  # django-voting
    'vote',    # our wrapper around django-voting
)

# Why does ugettext break things?!
ugettext = lambda s: s

LANGUAGES = (
    ('ar', u'العربية'),
    ('de', u'Deutsch'),
    ('en', u'English'),
    ('es', u'Español'),
    ('fr', u'Français'),
#    ('hr', 'Croatian'),
    ('hu', u'Magyar'),
    ('it', u'Italiano'),
    ('ja', u'日本語'),
    ('ko', u'한국어'),
#    ('mk', 'Macedonian'),
    ('nl', u'Nederlands'),
    ('pt', u'Português'),
    ('zh-Hant', u'正體中文'),
    ('zh-Hans', u'简体中文'),
#    ('zh', u'Chinese'),
#    ('ru', 'Russian'),
#    ('sr', 'Serbian'),
#    ('tr', 'Turkish'),
)

CACHE_BACKEND="memcached://127.0.0.1:11211"

