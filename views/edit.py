from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
import json
import oauth2


def edit(request):
    #Required settings for the client
    if not hasattr(settings, 'SS_WEB_SERVER_HOST'):
        raise(Exception("Required setting missing: SS_WEB_SERVER_HOST"))
    consumer = oauth2.Consumer(key=settings.SS_WEB_OAUTH_KEY, secret=settings.SS_WEB_OAUTH_SECRET)
    client = oauth2.Client(consumer)

    qargs = []
    space_ids = request.POST.getlist('space_id')
    for i in space_ids:
        qargs.append("id=%s" % i)
    qargs.append("limit=0")
    query = ''
    query = '&'.join(qargs)

    url = "%s/api/v1/schema" % settings.SS_WEB_SERVER_HOST
    client = oauth2.Client(consumer)
    resp, content = client.request(url, 'GET')
    schema = json.loads(content)
    url = "%s/api/v1/spot?%s" % (settings.SS_WEB_SERVER_HOST, query)
    resp, content = client.request(url, 'GET')
    spaces = json.loads(content)

    try:
        fixed = settings.SPACE_TABLE_KEYS['FIXED']
    except:
        fixed = ('id', 'name')
    try:
        scrollable = settings.SPACE_TABLE_KEYS['SCROLLABLE']
    except:
        scrollable = ('type',
                      'capacity',
                      'manager',
                      'last_modified',)
    leftover_keys = []
    for key in schema:
        if key not in fixed and key not in scrollable:
            leftover_keys.append(key)

    args = {
        "schema": schema,
        "spaces": spaces,
        "fixed_keys": fixed,
        "scrollable_keys": scrollable,
        "leftover_keys": leftover_keys,
    }

    context = RequestContext(request, {})
    return render_to_response('edit.html', args, context)
