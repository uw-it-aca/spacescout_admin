from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from spacescout_admin.utils import write_xls, write_csv
import json
import oauth2 as oauth


def download(request):
    context = RequestContext(request, {})

    # Required settings for the client
    if not hasattr(settings, 'SS_WEB_SERVER_HOST'):
        raise(Exception("Required setting missing: SS_WEB_SERVER_HOST"))
    if request.method == 'POST':
        consumer = oauth.Consumer(key=settings.SS_WEB_OAUTH_KEY, secret=settings.SS_WEB_OAUTH_SECRET)
        client = oauth.Client(consumer)
        url = "%s/api/v1/spot/all" % settings.SS_WEB_SERVER_HOST
        resp, content = client.request(url, "GET", headers={"XOAUTH_USER": "%s" % request.user, "Content-Type": "application/json", "Accept": "application/json"})
        if content:
            spots = json.loads(content)
            if 'csv' in request.POST:
                response = write_csv(spots)
                return response
            elif 'xls' in request.POST:
                response = write_xls(spots)
                return response
    return render_to_response('download.html', context)
