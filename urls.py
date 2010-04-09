from django.conf.urls.defaults import *
from django.conf import settings

from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

from account.openid_consumer import PinaxConsumer


if settings.ACCOUNT_OPEN_SIGNUP:
    signup_view = "account.views.signup"
else:
    signup_view = "signup_codes.views.signup"


urlpatterns = patterns('',
    url(r'^$', 'commonsense.views.main_page', name='home'),
    
    url(r'^admin/invite_user/$', 'signup_codes.views.admin_invite_user', name="admin_invite_user"),
    url(r'^account/signup/$', signup_view, name="acct_signup"),
    
    (r'^about/', include('about.urls')),
    (r'^account/', include('account.urls')),
    (r'^openid/(.*)', PinaxConsumer()),
    (r'^profiles/', include('basic_profiles.urls')),
    (r'^notices/', include('notification.urls')),
    (r'^announcements/', include('announcements.urls')),
    
    (r'^admin/(.*)', admin.site.root),

    (r'^vote/', include('vote.urls')),
    (r'^api/', include('csc.webapi.urls')),
    (r'^usertest/', include('usertest.urls')),
    (r'^colorizer/', include('colorizer.urls')),
    (r'^en/colorizer/', include('colorizer.urls')), # backwards compatible
    (r'^analogyspace/', include('analogyspace.urls')),
)

langs = '|'.join(lang for lang, _ in settings.LANGUAGES)
urlpatterns += [url('^(?P<lang>%s)/' % langs, include('commonsense.urls_lang'))]

if settings.SERVE_MEDIA:
    urlpatterns += patterns('',
        (r'^site_media/', include('staticfiles.urls')),
    )
