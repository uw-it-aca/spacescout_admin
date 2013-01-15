from django.shortcuts import render_to_response
from django.template import RequestContext


def edit_space(request, spot_id):
    context = RequestContext(request, {})
    return render_to_response('edit_space.html', context)
