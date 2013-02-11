from spacescout_admin.forms import QueueForm
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
import json
import oauth2


#@login_required
def edit_space(request, spot_id):
    if request.POST:
        space_datum = {}
        for key in request.POST:
            space_datum[key] = request.POST[key]
        data = {'space_id': int(space_datum['id']),
                'json': json.dumps(space_datum),
                'status': 'updated', }
        form = QueueForm(data)
        if form.is_valid():
            form.save()
        else:
            #TODO: do something appropriate if the form isn't valid
            pass
        url = '/space/%s' % space_datum['id']
        return HttpResponseRedirect(url)
    else:
        #Required settings for the client
        if not hasattr(settings, 'SS_WEB_SERVER_HOST'):
            raise(Exception("Required setting missing: SS_WEB_SERVER_HOST"))
        consumer = oauth2.Consumer(key=settings.SS_WEB_OAUTH_KEY, secret=settings.SS_WEB_OAUTH_SECRET)
        url = "%s/api/v1/schema" % settings.SS_WEB_SERVER_HOST
        client = oauth2.Client(consumer)
        resp, content = client.request(url, 'GET')
        schema = json.loads(content)
        spot_url = "%s/api/v1/spot/%s" % (settings.SS_WEB_SERVER_HOST, spot_id)
        resp, content = client.request(spot_url, 'GET')
        spot = json.loads(content)

        args = {
            "schema": schema,
            "spot": spot,
        }

        context = RequestContext(request, {})
        return render_to_response('edit_space.html', args, context)
