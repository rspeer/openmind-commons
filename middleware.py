from django.utils import translation

# http://www.djangosnippets.org/snippets/684/
class SetTestCookieMiddleware(object):
    def process_request(self, request):
        if not request.user.is_authenticated():
            request.session.set_test_cookie()


class LanguageOverrideMiddleware:
    def process_view(self, request, view_func, view_args, view_kwargs):
        '''Override the Django UI language to match the language passed
        in the URL.'''
        lang_code = view_kwargs.get('lang', None)
        if lang_code is None:
            return None

        # FIXME: check that lang_code is a valid language.
        translation.deactivate()
        translation.activate(lang_code)
        request.LANGUAGE_CODE = lang_code
        request.session['django_language'] = lang_code
        return None

        ''' this is for if we want to override the locale middleware.
        from django.conf import settings
        from django.utils.translation import check_for_language, activate

        supported = dict(settings.LANGUAGES)
        if lang_code in supported and lang_code is not None and check_for_language(lang_code):
            activate(lang_code)
            request.
        return None'''
