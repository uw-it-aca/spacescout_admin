from django.shortcuts import render_to_response
from django.template import RequestContext


def edit(request):
    context = RequestContext(request, {})

    checked_count = int(request.POST['checked_spaces'])
    context['count'] = [i + 1 for i in range(checked_count)]

    return render_to_response('edit.html', context)
