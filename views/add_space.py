from django.shortcuts import render_to_response
from django.template import RequestContext


def add_space(request):
    context = RequestContext(request, {})
    return render_to_response('add_space.html', context)
