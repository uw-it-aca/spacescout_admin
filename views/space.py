""" Copyright 2012, 2013 UW Information Technology, University of Washington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from spacescout_admin.models import *
from spacescout_admin.spot import Spot, SpotException
from spacescout_admin.space_map import SpaceMap, SpaceMapException
from spacescout_admin.rest_dispatch import RESTDispatch
from spacescout_admin.oauth import oauth_initialization
from spacescout_admin.permitted import Permitted, PermittedException
from spacescout_admin.views.schema import SpotSchema, SpotSchemaException
import simplejson as json


class SpaceManager(RESTDispatch):
    """ Performs query of Admin models at /api/v1/admins/?.
        GET returns 200 with Admin models
    """
    def __init__(self):
        self._spacemap = SpaceMap()

    def GET(self, args, **kwargs):
        if 'space_id' in kwargs:
            return self._space_detail(kwargs['space_id'])

        return self._space_list()

    def PUT(self, args, **kwargs):
        try:
            # partial representation allowed
            # only space.pending is written
            schema = SpotSchema().get()
            space_id = kwargs['space_id']
            space = Space.objects.get(id=space_id)
            if space.spot_id:
                spot = Spot().get(space.spot_id)
            else:
                spot = self._spacemap.pending_spot(space, schema)

            Permitted().edit(self._request.user, space, spot)
            data = json.loads(self._request.read())
            fields, missing_fields = self._validate(spot, data)

            pending = json.loads(space.pending) if space.pending else {}

            for field in fields:
                pending[field] = fields[field]

            if len(missing_fields) > 0:
                space.is_complete = None
                pending['_missing_fields'] = []
                pending['_missing_fields'] = missing_fields
            else:
                space.is_complete = True

            space.pending = json.dumps(pending) if len(pending) > 0 else None
            space.save()
            return self.json_response(json.dumps('{"id": "%s"}' % space.id))
        except PermittedException:
            return self.error_response(401, "Unauthorized")
        except Space.DoesNotExist:
            if e.args[0]['status_code'] == 404:
                self.error404_response()
                # no return
        except (SpaceMapException, SpotException, SpotSchemaException) as e:
            return self.error_response(e.args[0]['status_code'],
                                       e.args[0]['status_text'])

    def POST(self, args, **kwargs):
        try:
            Permitted().create(self._request.user)
            schema = SpotSchema().get()
            space = Space(manager=self._request.user,
                          modified_by=self._request.user)
            spot = self._spacemap.pending_spot(space, schema)
            data = json.loads(self._request.read())

            fields, missing_fields = self._validate(spot, data)
            pending = {}
            for field in fields:
                pending[field] = fields[field]

            if len(missing_fields) > 0:
                space.is_complete = None
                pending['_missing_fields'] = []
                pending['_missing_fields'] = missing_fields
            else:
                space.is_complete = True

            for field in settings.SS_SPACE_CREATION_FIELDS:
                if 'value' in field and 'key' in field['value']:
                    key = field['value']['key']
                    if 'required' in field and (key not in data or bool(data[key]) == False):
                        return self.error_response(400, "Bad Request")

            space.pending = json.dumps(pending) if len(pending) > 0 else None

            space.save()
            return self.json_response(json.dumps('{"id": "%s"}' % space.id))
        except PermittedException:
            return self.error_response(401, "Unauthorized")

    def _validate(self, spot, data):
        fields = {}
        missing_fields = []
        seen_fields = {}
        for section in settings.SS_SPACE_DEFINITIONS:
            for field in section['fields'] if 'fields' in section else []:
                for value in field['value'] if isinstance(field['value'], list) else [field['value']]:
                    key = value['key']
                    val = data[key] if key in data else None
                    orig_val = self._spot_value(key, spot)
                    if key in data and val != orig_val:
                        fields[key] = val

                    if 'required' in field and bool(val) == False and bool(orig_val) == False:
                        s = section.get('section')
                        f = field.get('name')
                        if s + f not in seen_fields:
                            missing_fields.append({ 'section': s, 'field': f })
                            seen_fields[s + f] = True

        if 'available_hours' in data:
            valid_hours = True
            for d in data['available_hours']:
                for h in data['available_hours'][d]:
                    if len(h) == 2:
                        if int("".join(h[0].split(":"))) >= int("".join(h[1].split(":"))):
                            valid_hours = False
                    else:
                        valid_hours = False

            if valid_hours:
                fields['available_hours'] = data['available_hours']

        return fields, missing_fields

    def _space_detail(self, space_id):
        try:
            schema = SpotSchema().get()
            space_model = Space.objects.get(id=space_id)
            if space_model.spot_id:
                spot = Spot().get(space_model.spot_id)
            else:
                spot = self._spacemap.pending_spot(space_model, schema)

            Permitted().view(self._request.user, space_model, spot)

            return self.json_response(json.dumps(self._spacemap.space_rep(space_model, spot, schema)))
        except Space.DoesNotExist:
            self.error404_response()
        except PermittedException:
            return self.error_response(401, "Unauthorized")
        except (SpaceMapException, SpotException, SpotSchemaException) as e:
            return self.error_response(e.args[0]['status_code'],
                                       e.args[0]['status_text'])

    def _space_list(self):
        filter = {}
        published = True
        complete = True
        json_rep = []
        seen = {}

        try:
            schema = SpotSchema().get()
        except SpotSchemaException as e:
            return self.error_response(e.args[0]['status_code'],
                                       e.args[0]['status_text'])

        if 'published' in self._request.GET:
            p = self._request.GET.get('published')
            published = True if (p == '1' or p.lower() == 'true') else False
            filter['spot_id__isnull'] = True if (not published) else False

        if 'complete' in self._request.GET:
            i = self._request.GET.get('complete')
            complete = (i == '1' or i.lower() == 'true')
            filter['spot_id__isnull'] = True
            if not complete:
                filter['is_complete__isnull'] = True
            else:
                filter['is_complete'] = True

        if published:
            search_args = {
                #'manager': '',
                #'editors': '',
                'limit': '0'
            }

            try:
                spots = self._get_spots(search_args)
            except Exception, errstr:
                return self.error_response(500, ("%s" % (errstr)))

            for spot in spots:
                try:
                    spot_id = spot.get('id')
                    try:
                        space = Space.objects.get(spot_id=spot_id)
                    except Space.DoesNotExist:
                        space = Space(spot_id=spot_id,
                                      manager=spot.get('manager'),
                                      is_complete=True)
                        space.save()

                    Permitted().view(self._request.user, space, spot)
                    seen[str(spot_id)] = 1
                    json_rep.append(self._spacemap.space_rep(space, spot, schema))
                except PermittedException:
                    pass
                except SpaceMapException as e:
                    return self.error_response(e.args[0]['status_code'],
                                               e.args[0]['status_text'])

        for space in Space.objects.filter(**filter):
            if str(space.spot_id) in seen:
                continue

            try:
                if space.spot_id:
                    spot = Spot().get(space.spot_id)
                else:
                    spot = self._spacemap.pending_spot(space, schema)

                Permitted().view(self._request.user, space, spot)
                json_rep.append(self._spacemap.space_rep(space, spot, schema))
            except PermittedException:
                pass
            except SpaceMapException as e:
                return self.error_response(e.args[0]['status_code'],
                                           e.args[0]['status_text'])

        return self.json_response(json.dumps(json_rep))

    def _get_spots(self, search_args):
        consumer, client = oauth_initialization()

        #for key in options:
        #    if isinstance(options[key], types.ListType):
        #        for item in options[key]:
        #            args.append("{0}={1}".format(urllib.quote(key), urllib.quote(item)))
        #    else:
        #        args.append("{0}={1}".format(urllib.quote(key), urllib.quote(options[key])))

        #url = "{0}/api/v1/spot/search?{1}".format(settings.SS_WEB_SERVER_HOST, "&".join(search_args))
        url = "{0}/api/v1/spot/all".format(settings.SS_WEB_SERVER_HOST, "&".join(search_args))

        resp, content = client.request(url, 'GET')

        if resp.status != 200:
            Exception("Unable to load spots")

        i18n_json = []
        permitted = Permitted()
        for spot in json.loads(content):
            try:
                permitted.view(self._request.user, {}, spot)
                string_val = ''
                for x in range(0, len(spot['type'])):
                    if x is 0:
                        string_val = _(spot['type'][x])
                    else:
                        string_val = string_val + ', ' + _(spot['type'][x])
    
                    spot['type'] = string_val
                    i18n_json.append(spot)
            except PermittedException:
                pass

        return i18n_json

    def _spot_value(self, key, spot):
        return self._spacemap.get_by_keylist(key.split('.'), spot)
