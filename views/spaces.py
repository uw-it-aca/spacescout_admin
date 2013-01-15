from django.shortcuts import render_to_response
from django.template import RequestContext


def spaces(request):
    context = RequestContext(request, {})
    return render_to_response('spaces.html', context)
