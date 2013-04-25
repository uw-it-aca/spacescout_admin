from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from spacescout_admin.models import QueuedSpace
import oauth2
import json


@login_required
def spaces(request):
    #Required settings for the client
    if not hasattr(settings, 'SS_WEB_SERVER_HOST'):
        raise(Exception("Required setting missing: SS_WEB_SERVER_HOST"))
    consumer = oauth2.Consumer(key=settings.SS_WEB_OAUTH_KEY, secret=settings.SS_WEB_OAUTH_SECRET)
    url = "%s/api/v1/schema" % settings.SS_WEB_SERVER_HOST
    client = oauth2.Client(consumer)
    resp, content = client.request(url, 'GET')
    schema = json.loads(content)
    spot_url = "%s/api/v1/spot/all" % settings.SS_WEB_SERVER_HOST
    resp, content = client.request(spot_url, 'GET')
    spots = json.loads(content)
    q_spots_status = {}
    for q_spot in QueuedSpace.objects.all():
        q_spots_status.update({q_spot.space_id: q_spot.status})
    context = RequestContext(request, {})
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
    args = {
        "schema": schema,
        "spots": spots,
        "q_spots_status": q_spots_status,
        "fixed_keys": fixed,
        "scrollable_keys": scrollable,
    }
    return render_to_response('spaces.html', args, context)
