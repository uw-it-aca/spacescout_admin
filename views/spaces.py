from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
import oauth2
import json


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
    context = RequestContext(request, {})
    args = {
        "schema": schema,
        "spots": spots,
        "fixed_keys": ('id', 'name',),
        "scrollable_keys": ('type', )
    }
    return render_to_response('spaces.html', args, context)
