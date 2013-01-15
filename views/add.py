from django.shortcuts import render_to_response
from django.template import RequestContext


def add(request):
    context = RequestContext(request, {})
    return render_to_response('add.html', context)
