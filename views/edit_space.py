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
        post = dict(request.POST.viewitems())
        for key in post:
            # Since everything's coming back from the form fields as text, try to convert
            # the strings to the appropriate type
            space_datum[key] = autoconvert(post[key])
        cleaned_space_datum = _cleanup(space_datum)
        data = {'space_id': space_datum['id'], 'json': cleaned_space_datum}
        # if we got the space from the queue, edit it rather than create a new instance
        if 'q_id' in space_datum:
            q_obj = QueuedSpace.objects.get(pk=int(request.POST["q_id"]))
            if json.loads(q_obj.json) == json.loads(cleaned_space_datum):
                data.update({'status': q_obj.status, 'errors': q_obj.errors})
            else:
                data.update({'status': 'updated', 'errors': '{}'})
            form = QueueForm(data, instance=q_obj)
        else:
            data.update({'status': 'updated', 'errors': '{}'})
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
            if 'changed' in space_datum and not json.loads(queued.errors):
                if space_datum['changed'] == 'approved':
                    queued.status = 'approved'
                    queued.approved_by = request.user
                elif space_datum['changed'] == 'publish':
                    response = upload_data(request, [{'data': queued.json, 'id': spot_id}])  # PUT if spot_id, POST if not spot_id
                    if not response['failure_descs']:  # if there are no failures
                        QueuedSpace.objects.get(space_id=spot_id).delete()
                        return HttpResponseRedirect('/')
                    else:
                        errors = {}
                        for failure in response['failure_descs']:
                            if type(failure['freason']) == list:
                                errors.update({failure['flocation']: []})
                                for reason in failure['freason']:
                                    errors[failure['flocation']].append(reason)
                            else:
                                errors.update({failure['flocation']: failure['freason']})
                        queued.errors = json.dumps(errors)
                        queued.status = 'updated'
                        queued.approved_by = None
                        queued.save()
                        url = '/space/%s' % space_datum['id']
                        return HttpResponseRedirect(url)
            elif 'changed' in space_datum and queued.errors:
                url = '/space/%s' % space_datum['id']
                return HttpResponseRedirect(url)
            else:
                if data['status'] == 'approved':
                    queued.approved_by = QueuedSpace.objects.get(space_id=spot_id).approved_by
                else:
                    queued.approved_by = None
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
            errors = json.loads(spot.errors)
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
            errors = None

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
            "errors": errors,
        }

        context = RequestContext(request, {})
        return render_to_response('edit_space.html', args, context)


def autoconvert(s):
    """ Takes a string and tries to return a non-string datatype (int, float, list, etc.)
        If it can't, returns the string.
    """
    try:
        if type(s).__name__ == 'list' and len(s) == 1:
            s = s[0]
    except:
        pass
    try:
        if type(eval(s)).__name__ == 'builtin_function_or_method':
            return s
        else:
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
    for key in schema:
        if type(schema[key]).__name__ == 'dict':
            for subkey in schema[key]:
                if subkey in bad_json:
                    if key not in good_json:
                        good_json.update({key: {}})
                    if not schema[key][subkey] == 'auto':
                        good_json[key].update({subkey: bad_json[subkey]})
    for key in bad_json:
        if key in schema and schema[key] != 'auto':
            good_json.update({key: bad_json[key]})
    return json.dumps(good_json)
