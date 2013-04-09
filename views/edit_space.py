from spacescout_admin.forms import QueueForm
from spacescout_admin.models import QueuedSpace
from spacescout_admin.utils import upload_data
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
import json
import oauth2


@login_required
def edit_space(request, spot_id):
    if request.POST:
        space_datum = {}
        for key in request.POST:
            # Since everything's coming back from the form fields as text, try to convert
            # the strings to the appropriate type
            space_datum[key] = autoconvert(request.POST[key])
        cleaned_space_datum = _cleanup(space_datum)
        data = {'space_id': int(space_datum['id']),
                'json': cleaned_space_datum}
        # if we got the space from the queue, edit it rather than create a new instance
        if 'q_id' in space_datum:
            q_obj = QueuedSpace.objects.get(pk=int(request.POST["q_id"]))
            if json.loads(q_obj.json) == json.loads(cleaned_space_datum):
                data.update({'status': q_obj.status})
            else:
                data.update({'status': 'updated'})
            form = QueueForm(data, instance=q_obj)
        else:
            data.update({'status': 'updated'})
            form = QueueForm(data)
        if form.is_valid():
            queued = form.save(commit=False)
            queued.modified_by = request.user
            if 'q_id' in space_datum:
                queued.space_etag = QueuedSpace.objects.get(space_id=spot_id).space_etag
                queued.space_last_modified = QueuedSpace.objects.get(space_id=spot_id).space_last_modified
            else:
                queued.space_etag = space_datum['space_etag']
                queued.space_last_modified = space_datum['space_last_modified']
            try:
                approved = QueuedSpace.objects.get(space_id=spot_id).approved_by
            except:
                approved = None
            if 'changed' in space_datum:
                if space_datum['changed'] == 'approved':
                    queued.status = 'approved'
                    queued.approved_by = request.user
                elif space_datum['changed'] == 'publish':
                    spot = QueuedSpace.objects.get(space_id=spot_id)
                    response = upload_data(request, [{'data': spot.json, 'id': spot_id}])  # PUT if spot_id, POST if not spot_id
                    if not response['failure_descs']:  # if there are no failures
                        QueuedSpace.objects.get(space_id=spot_id).delete()
                        return HttpResponseRedirect('/')
                    else:
                        for failure in response['failure_descs']:
                            failure
                            #print '\n'
                            #print 'spot: ' + failure['fname'] + '\n' + 'location: ' + failure['flocation']
                            #for reason in failure['freason']:
                            #    print 'reason: ' + reason
                            #print '\n'
                        #blow up and throws some phat errors, yo!
            elif approved:
                queued.approved_by = approved
            queued.save()
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
            modified_by = spot.modified_by
            approved_by = spot.approved_by
            last_modified = spot.last_modified
            status = spot.status
            space_etag = spot.space_etag
            space_last_modified = spot.space_last_modified
            spot = json.loads(spot.json)
        except:
            spot_url = "%s/api/v1/spot/%s" % (settings.SS_WEB_SERVER_HOST, spot_id)
            resp, content = client.request(spot_url, 'GET')
            spot = json.loads(content)
            q_id = None
            modified_by = None
            approved_by = "an admin"
            status = None
            space_etag = resp['etag']
            last_modified = None
            space_last_modified = spot["last_modified"]

        args = {
            "spot_id": spot_id,
            "schema": schema,
            "spot": spot,
            "q_id": q_id,
            "updated_by": modified_by,
            "approved_by": approved_by,
            "last_modified": last_modified,
            "status": status,
            "space_etag": space_etag,
            "space_last_modified": space_last_modified,
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


def _cleanup(bad_json):
    """ Takes the json in spot.json and returns json that is kosher with Spotseeker_Server
    """
    #Required settings for the client
    if not hasattr(settings, 'SS_WEB_SERVER_HOST'):
        raise(Exception("Required setting missing: SS_WEB_SERVER_HOST"))
    consumer = oauth2.Consumer(key=settings.SS_WEB_OAUTH_KEY, secret=settings.SS_WEB_OAUTH_SECRET)
    url = "%s/api/v1/schema" % settings.SS_WEB_SERVER_HOST
    client = oauth2.Client(consumer)
    resp, content = client.request(url, 'GET')
    schema = json.loads(content)
    good_json = {}
    for key in bad_json:
        if key in schema and schema[key] != 'auto':
            good_json.update({key: bad_json[key]})
    return json.dumps(good_json)
