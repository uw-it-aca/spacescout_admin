from spacescout_admin.forms import QueueForm
from spacescout_admin.models import QueuedSpace
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
            # Since everything's coming back from the form fields as text, try to convert
            # the strings to the appropriate type
            space_datum[key] = autoconvert(request.POST[key])
        data = {'space_id': int(space_datum['id']),
                'json': json.dumps(space_datum),
                'status': 'updated', }
        # if we got the space from the queue, edit it rather than create a new instance
        if request.POST["q_id"]:
            q_obj = QueuedSpace.objects.get(pk=int(request.POST["q_id"]))
            form = QueueForm(data, instance=q_obj)
        else:
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

        try:
            spot = QueuedSpace.objects.get(space_id=spot_id)
            q_id = spot.pk
            spot = json.loads(spot.json)
        except:
            spot_url = "%s/api/v1/spot/%s" % (settings.SS_WEB_SERVER_HOST, spot_id)
            resp, content = client.request(spot_url, 'GET')
            spot = json.loads(content)
            q_id = None

        args = {
            "schema": schema,
            "spot": spot,
            "q_id": q_id,
        }

        context = RequestContext(request, {})
        return render_to_response('edit_space.html', args, context)


def autoconvert(s):
    """ Takes a string and tries to return a non-string datatype (int, float, list, etc.)
        If it can't, returns the string.
    """
    try:
        return eval(s)
    except:
        return s
