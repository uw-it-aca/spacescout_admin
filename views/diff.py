from django.contrib.auth.decorators import login_required
from spacescout_admin.models import QueuedSpace
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
import oauth2
import json


@login_required
def diff(request, spot_id):
    #Required settings for the client
    if not hasattr(settings, 'SS_WEB_SERVER_HOST'):
        raise(Exception("Required setting missing: SS_WEB_SERVER_HOST"))
    consumer = oauth2.Consumer(key=settings.SS_WEB_OAUTH_KEY, secret=settings.SS_WEB_OAUTH_SECRET)
    url = "%s/api/v1/schema" % settings.SS_WEB_SERVER_HOST
    client = oauth2.Client(consumer)
    resp, content = client.request(url, 'GET')
    schema = json.loads(content)
    try:
        json_in_db = json.loads(QueuedSpace.objects.get(space_id=spot_id).json)
    except:
        json_in_db = None
    if 'failed_json' in request.GET:
        failed_json = json.loads(dict(request.GET.viewitems())['failed_json'][0])
    else:
        failed_json = None
    args = {
        'schema': schema,
        'spot_id': spot_id,
        'json_in_db': json_in_db,
        'failed_json': failed_json,
    }
    context = RequestContext(request, {})
    return render_to_response('diff.html', args, context)
