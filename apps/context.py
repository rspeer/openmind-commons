from django.http import HttpResponse
from django.utils import simplejson
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

def respond_with(template, request, new_data):
    '''Respond to the request with the given template and data. Uses the data from
    _common_data as a base; new_data can override.'''
    
    # Determine the format (HTML or JSON).
    format = request.GET.get('format', 'html')

    # Set the language code of the interface to match the data.
    if 'lang' in new_data:
        request.LANGUAGE_CODE = new_data['lang']
        if new_data['lang'] == 'pt':
            request.LANGUAGE_CODE = 'pt_BR'
            
    # Is this a JSON response? Yay.
    if format == 'json':
        new_data.setdefault('result', 'ok')
        if 'request' in new_data: del new_data['request']
        json = simplejson.dumps(new_data)
        return HttpResponse(json, mimetype='application/json', status=status)
        
    template_data = RequestContext(request, new_data)
    return render_to_response(template, template_data)

def commons_context(request):
    '''Return the common data we need for responding to a request.'''
    return {
        'is_devel': settings.DEVEL,
        'path': request.path,
        'lang': request.LANGUAGE_CODE,  # Specific views should override this.
        'langs': [dict(id=id, name=_(name),
                       is_cur=(request.LANGUAGE_CODE==id))
                  for id, name in settings.LANGUAGES]
        }
