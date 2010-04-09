# A collection of decorators and utility functions.
from django.http import HttpResponse
from django.utils import simplejson
from django.conf import settings
from django.template import loader, RequestContext
from django.core.cache import cache
from django.utils.translation import ugettext as _

# For error handling
from django.db.models.base import ObjectDoesNotExist

import re
import sys

from csc.util import cached

#########
## Here are two things that replace built-in Django functionality for some reason.
## FIXME: consider submitting these.
#########

# customized to enable setting status code.
def direct_to_template(request, template, extra_context=None, mimetype=None, status=200, **kwargs):
    """
    Render a given template with any extra URL parameters in the context as
    ``{{ params }}``.
    """
    if extra_context is None: extra_context = {}
    dictionary = {'params': kwargs}
    for key, value in extra_context.items():
        if callable(value):
            dictionary[key] = value()
        else:
            dictionary[key] = value
    c = RequestContext(request, dictionary)
    t = loader.get_template(template)
    return HttpResponse(t.render(c), mimetype=mimetype, status=status)


class OperationDisabledError(StandardError):
    def __init__(self, oper):
        self.oper = oper
    def __str__(self):
        return 'Operation disabled: '+self.oper


class needs_setting:
    '''Decorator to ensure that a function is never called if a setting is
    disabled.'''
    def __init__(self, setting, operation):
        self.setting = setting
        self.operation = operation
    def __call__(self, func):
        if getattr(settings, self.setting, False):
            return func
        def failing_func(request, *a, **kw):
            if hasattr(request, 'user') and request.user.is_staff:
                return func(request, *a, **kw)
            raise OperationDisabledError(self.operation)
        return failing_func


class InputError(Exception):
    should_log = False
    http_code = 400

class ParameterMissingError(InputError):
    def __init__(self, param):
        InputError.__init__(self, _('Required parameter missing: %s') % param)

def get_parameter(dct, elem, cast=None):
    if elem not in dct: raise ParameterMissingError(elem)
    res = dct[elem]
    if cast is None:
        return res
    else:
        try:
            return cast(res)
        except Exception, e:
            raise InputError(str(e))

from functools import wraps
def json_view(func):
    @wraps(func)
    def wrap(request, *a, **kw):
        response = None
        status = 200
        try:
            response = func(request, *a, **kw)
            assert isinstance(response, dict)
            response.setdefault('result', 'ok')
        except ObjectDoesNotExist, e:
            response = {'result': 'error',
                        'text': str(e)}
            status = 404
        except Exception, e:
            if settings.DEBUG: raise
            if not hasattr(e, 'http_code'):
                raise # It's a bug.

            # Always return a JSON response.
            msg = getattr(e, 'message', _('Internal error')+': '+str(e))
            response = {'result': 'error', 'text': msg}
            status = e.http_code
            
        json = simplejson.dumps(response)
        return HttpResponse(json, mimetype='application/json', status=status)
    return wrap

