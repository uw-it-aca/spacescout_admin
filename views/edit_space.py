from spacescout_admin.forms import QueueForm
from spacescout_admin.models import QueuedSpace
from spacescout_admin.utils import upload_data, to_datetime_object
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
import json
import oauth2


@login_required
def edit_space(request, spot_id):
    user = request.user
    has_a_perm = False
    can_reset = False
    can_update = False
    can_approve = False
    can_publish = False
    if user.has_perm('spacescout_admin.can_reset'):
        has_a_perm = True
        can_reset = True
    if user.has_perm('spacescout_admin.can_update'):
        has_a_perm = True
        can_update = True
    if user.has_perm('spacescout_admin.can_approve'):
        has_a_perm = True
        can_approve = True
    if user.has_perm('spacescout_admin.can_publish'):
        has_a_perm = True
        can_publish = True
    if user.has_perm('spacescout_admin.can_mod_any') or user.is_superuser:
        has_a_perm = True
        can_reset = True
        can_update = True
        can_approve = True
        can_publish = True

    #Required settings for the client
    if not hasattr(settings, 'SS_WEB_SERVER_HOST'):
        raise(Exception("Required setting missing: SS_WEB_SERVER_HOST"))
    consumer = oauth2.Consumer(key=settings.SS_WEB_OAUTH_KEY, secret=settings.SS_WEB_OAUTH_SECRET)
    url = "%s/api/v1/schema" % settings.SS_WEB_SERVER_HOST
    client = oauth2.Client(consumer)
    resp, content = client.request(url, 'GET')
    schema = json.loads(content)

    if request.POST and has_a_perm:
        space_datum = {}
        post = dict(request.POST.viewitems())
        for key in post:
            # All of the form field data comes back as lists of text. Converts to appropriate data types where possible
            space_datum[key] = _autoconvert(post[key])
        cleaned_space_datum = _cleanup(space_datum, schema)
        data = {'space_id': space_datum['id'], 'json': cleaned_space_datum}
        is_a_manager = _is_manager(user, space_datum['manager'])

        if _is_deleted(space_datum, is_a_manager, can_publish, user, spot_id, client):
            return HttpResponseRedirect('/')

        # If we got the space from the queue, edit it rather than create a new instance
        if 'q_id' in space_datum:
            try:
                q_obj = QueuedSpace.objects.get(pk=int(request.POST["q_id"]))
            except:
                error_message = 'Oops. Something went wrong. It appears that the spot you were attempting to modify is no longer in the database.'
                return HttpResponseRedirect('/error/%s?failed_json=%s&error_message=%s' % (spot_id, cleaned_space_datum, error_message))

            # If the json didn't change after the save click, keep the same status and errors as before
            if json.loads(q_obj.json) == json.loads(cleaned_space_datum):
                data.update({'status': q_obj.status, 'errors': q_obj.errors})
            else:
                data.update({'status': 'updated', 'errors': '{}'})
            q_etag = q_obj.q_etag
            form = QueueForm(data, instance=q_obj)

        # Creates a brand new spot
        else:
            data.update({'status': 'updated', 'errors': '{}'})
            q_etag = None
            form = QueueForm(data)

        # The user must be part of the group that has permission to edit the QueuedSpace - (is_a_manager)
        if form.is_valid() and is_a_manager:
            queued = form.save(commit=False)
            queued.modified_by = user

            if 'q_id' in space_datum:
                queued.space_etag = QueuedSpace.objects.get(space_id=spot_id).space_etag
                queued.space_last_modified = QueuedSpace.objects.get(space_id=spot_id).space_last_modified
            else:
                queued.space_etag = space_datum['space_etag']
                queued.space_last_modified = space_datum['space_last_modified']

            if q_etag:
                # The QueuedSpace etags must match in order to do anything
                if q_etag == space_datum['q_etag']:
                    no_errors = True
                    if json.loads(queued.errors):
                        no_errors = False

                    changed = False
                    if 'changed' in space_datum:
                        changed = True

                    # If the spot was approved, published, reset, or deleted
                    if changed:
                        is_reset = _is_reset(space_datum, can_reset, spot_id)
                        if is_reset:
                            return HttpResponseRedirect(is_reset)

                        # If trying to be approved or published and there are no errors
                        if no_errors:
                            queued = _is_approved(space_datum, can_approve, queued, user)
                            is_published = _is_published(request, space_datum, spot_id, can_publish, queued, schema)
                            if type(is_published).__name__ == 'unicode':
                                return HttpResponseRedirect(is_published)
                            else:
                                queued = is_published

                        # If trying to be approved or published and there are errors, do nothing
                        elif changed and not no_errors:
                            url = '/space/%s' % space_datum['id']
                            return HttpResponseRedirect(url)
                        # If the QueuedSpace is just being saved, not approved or published
                        else:
                            if data['status'] == 'approved':
                                queued.approved_by = QueuedSpace.objects.get(space_id=spot_id).approved_by
                            else:
                                queued.approved_by = None
                    queued.save()
                # If the QueuedSpace etags do not match
                else:
                    return HttpResponseRedirect('/error/%s?failed_json=%s' % (spot_id, queued.json))
                    # Could not figure out "return HttpResponseRedirect(reverse(error.error, blah, blah))"
                    # It would be really cool if we could figure out how to get this to work

            # If there is no QueuedSpace etag at all
            else:
                try:
                    # Checks to see if the same spot has been created while you were editing this one
                    QueuedSpace.objects.get(space_id=spot_id)
                    return HttpResponseRedirect('/error/%s?failed_json=%s' % (spot_id, queued.json))
                    # Same here, because passing a dict through the url is UUGGLLLYYY. It would be much
                    # cooler to pass the extra json straight to the error view
                except:
                    queued.save()

        # If the form is not valid or the user does not have permissions to modify this spot
        else:
            #TODO: do something appropriate if the form isn't valid
            pass

        url = '/space/%s' % space_datum['id']
        return HttpResponseRedirect(url)

    else:
        from_queued_space = False
        try:
            spot = QueuedSpace.objects.get(space_id=spot_id)
            from_queued_space = True
        except:
            try:
                spot_url = "%s/api/v1/spot/%s" % (settings.SS_WEB_SERVER_HOST, spot_id)
                resp, content = client.request(spot_url, 'GET')
                spot = json.loads(content)
            except:
                return HttpResponseRedirect('/error/%s' % (spot_id))

        if from_queued_space:
            errors = json.loads(spot.errors)
            space_etag = spot.space_etag
            q_etag = spot.q_etag
            status = spot.status
            ugly_space_last_modified = spot.space_last_modified
            nice_space_last_modified = ugly_space_last_modified
            last_modified = spot.last_modified
            modified_by = spot.modified_by
            approved_by = spot.approved_by
            q_id = spot.pk
            spot = json.loads(spot.json)
        else:
            errors = None
            space_etag = resp['etag']
            q_etag = None
            status = None
            ugly_space_last_modified = spot['last_modified']
            nice_space_last_modified = to_datetime_object(ugly_space_last_modified)
            last_modified = None
            modified_by = None
            approved_by = None
            q_id = None
        is_a_manager = _is_manager(user, _autoconvert(spot['manager']))

        args = {
            "spot_id": spot_id,
            "user": user,
            "can_reset": can_reset,
            "can_update": can_update,
            "can_approve": can_approve,
            "can_publish": can_publish,
            "schema": schema,
            "spot": spot,
            "errors": errors,
            "space_etag": space_etag,
            "q_etag": q_etag,
            "status": status,
            "ugly_space_last_modified": ugly_space_last_modified,
            "nice_space_last_modified": nice_space_last_modified,
            "last_modified": last_modified,
            "updated_by": modified_by,
            "approved_by": approved_by,
            "q_id": q_id,
            "is_a_manager": is_a_manager,
        }

        context = RequestContext(request, {})
        return render_to_response('edit_space.html', args, context)


def _autoconvert(s):
    """ Takes a string and tries to return a non-string datatype (int, float, list, etc.)
        If it can't, returns the string.
    """
    try:
        if type(s).__name__ == 'list' and len(s) == 1:
            s = s[0]
    except:
        pass

    try:
        # makes sure a python function or object is not added to the list
        if type(eval(s)).__name__ == 'builtin_function_or_method':
            return s
        else:
            return eval(s)
    except:
        return s


def _cleanup(bad_json, schema):
    """ Takes the json in spot.json and returns json that is kosher with the SS_WEB_SERVER schema
    """
    good_json = {}

    # Loops throught the dicts in the schema and adds any key/values in
    # the json parameter that should be in a dict into the correct dict
    # according to the schema
    for key in schema:
        if type(schema[key]).__name__ == 'dict':
            for subkey in schema[key]:
                if subkey in bad_json:
                    not_a_list = False
                    valid_list_value = False
                    if not type(schema[key][subkey]).__name__ == 'list':
                        not_a_list = True
                    else:
                        if bad_json[subkey] in schema[key][subkey]:
                            valid_list_value = True
                    if not_a_list or valid_list_value:
                        if key not in good_json:
                            good_json.update({key: {}})
                        if not schema[key][subkey] == 'auto':
                            good_json[key].update({subkey: bad_json[subkey]})

    # Loops through all of the json parameter and only adds data that
    # is in the schema except for data the server auto adds
    for key in bad_json:
        if key in schema and schema[key] != 'auto':
            good_json.update({key: bad_json[key]})

    return json.dumps(good_json)


def _is_manager(user, managers):
    """ Takes a list of groups and users and checks to see if the user passed
        in is any of those groups or if the user is a superuser
    """
    is_a_manager = False

    # if the value is a list
    if type(managers).__name__ == 'list':
        for group in managers:
            try:
                # if the list item is a group
                if user in Group.objects.get(name=group).user_set.all():
                    is_a_manager = True
            except:
                # if the list item is not a group, but just a username
                if user.username == group:
                    is_a_manager = True
    else:  # the value should just be a string if it is not a list
        try:
            # if the value is the name of a group
            if user in Group.objects.get(name=managers).user_set.all():
                is_a_manager = True
        except:
            # if the value is just a username
            if user.username == managers:
                is_a_manager = True

    if user.has_perm('spacescout_admin.can_mod_any') or user.is_superuser:
        is_a_manager = True

    return is_a_manager


def _is_deleted(space_datum, is_a_manager, can_publish, user, spot_id, client):
    # Completely deletes the spot from the server
    if 'changed' in space_datum and space_datum['changed'] == 'delete':
        if is_a_manager and can_publish:
            spot_url = "%s/api/v1/spot/%s" % (settings.SS_WEB_SERVER_HOST, space_datum['id'])
            spot_headers = {
                "XOAUTH_USER": "%s" % user,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "If_Match": space_datum['space_etag'],
            }
            response = client.request(spot_url, 'DELETE', headers=spot_headers)
            if 'q_id' in space_datum:
                QueuedSpace.objects.get(space_id=spot_id).delete()
            return True
    return False


def _is_reset(space_datum, can_reset, spot_id):
    # Undoes all saved changes made to the QueuedSpace
    if space_datum['changed'] == 'reset' and can_reset:
        QueuedSpace.objects.get(space_id=spot_id).delete()
        url = '/space/%s' % space_datum['id']
        return url
    return False


def _is_approved(space_datum, can_approve, queued, user):
    # Approves the QueuedSpace
    if space_datum['changed'] == 'approved' and can_approve:
        queued.status = 'approved'
        queued.approved_by = user
    return queued


def _is_published(request, space_datum, spot_id, can_publish, queued, schema):
    # Publishes the QueuedSpace
    if space_datum['changed'] == 'publish' and can_publish:
        # Attempts to put the spot to the server
        response = upload_data(request, [{
            'data': queued.json,
            'id': spot_id,
            'etag': queued.space_etag
        }])

        # If there are no failures, delete the QueuedSpace
        if not response['failure_descs']:
            QueuedSpace.objects.get(space_id=spot_id).delete()
            return u'/'
        # If there are errors, add them to the QueuedSpace errors field
        else:
            errors = {}
            for failure in response['failure_descs']:
                if type(failure['freason']) == list:
                    errors.update({failure['flocation']: []})
                    for reason in failure['freason']:
                        errors[failure['flocation']].append(reason)
                else:
                    errors.update({failure['flocation']: failure['freason']})
            for error in errors:
                # If errors are thrown in fields the user cant edit, return the error
                # page instead of adding them to the QueuedSpace error field
                if error in schema:
                    if schema[error] == 'auto':
                        return '/error/%s?failed_json=%s&error_message=%s' % (spot_id, queued.json, errors)
            queued.errors = json.dumps(errors)
            queued.status = 'updated'
            queued.approved_by = None
    return queued
