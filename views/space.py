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
            pending = json.loads(space.pending) if space.pending else {}
            data = json.loads(self._request.read())
            space.is_complete = True
            for section in settings.SS_SPACE_DEFINITIONS:
                for field in section['fields'] if 'fields' in section else []:
                    for value in field['value'] if isinstance(field['value'], list) else [field['value']]:
                        key = value['key']
                        val = data[key] if key in data else None
                        orig_val = self._spot_value(spot, key)
                        if key in data and val != orig_val:
                            pending[key] = val

                        if 'required' in field and ((val == None or len(val) == 0)
                                                    and (orig_val == None or len(orig_val) == 0)):
                            space.is_complete = None

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
                    pending['available_hours'] = data['available_hours']

            space.pending = json.dumps(pending) if len(pending) > 0 else None
            space.save()
            return self.json_response(json.dumps('{ ok: true }'))
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
            data = json.loads(self._request.read())
            pending = {}
            for field in settings.SS_SPACE_CREATION_FIELDS:
                if 'value' in field and 'key' in field['value']:
                    key = field['value']['key']
                    value = data[key] if key in data else None
                    if 'required' in field and value == None or len(str(value).strip()) == 0:
                        return self.error_response(400, "Bad Request")

                    if value:
                        pending[key] = value

            space = Space(manager=self._request.user,
                          modified_by=self._request.user,
                          pending=json.dumps(pending))
            space.save()
            return self.json_response(json.dumps('{ space_id: %s }' % space.id))
        except PermittedException:
            return self.error_response(401, "Unauthorized")

    def _space_detail(self, space_id):
        try:
            schema = SpotSchema().get()
            space_model = Space.objects.get(id=space_id)
            if space_model.spot_id:
                spot = Spot().get(space_model.spot_id)
            else:
                spot = self._spacemap.pending_spot(space_model, schema)

            Permitted().view(self._request.user, space_model, spot)
            space_rep = self._spacemap.space_representation(space_model, spot, schema)
            return self.json_response(json.dumps(space_rep))
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
                    json_rep.append(self._search_result(space, spot, schema))
                except PermittedException:
                    pass
                except SpaceMapException as e:
                    return self.error_response(e.args[0]['status_code'],
                                               e.args[0]['status_text'])

        for space in Space.objects.filter(**filter):
            if str(space.spot_id) in seen:
                continue

            try:
                Permitted().view(self._request.user, space, {})
                json_rep.append(self._search_result(space, None, schema))
            except PermittedException:
                pass
            except SpaceMapException as e:
                return self.error_response(e.args[0]['status_code'],
                                           e.args[0]['status_text'])

        return self.json_response(json.dumps(json_rep))

    def _search_result(self, space, spot, schema):
        if spot is None:
            spot = self._spacemap.pending_spot(space, schema)

        missing_sections = []
        missing_names = {}
        for secdef in settings.SS_SPACE_DEFINITIONS:
            for f in secdef['fields'] if 'fields' in secdef else []:
                if 'required' in f:
                    for v in f['value'] if isinstance(f['value'], list) else [f['value']]:
                        if not bool(self._spot_value(spot, v['key'])):
                            if secdef['section'] + f['name'] not in missing_names:
                                missing_names[secdef['section'] + f['name']] = True
                                missing_sections.append({
                                    'section': secdef['section'],
                                    'element': f['name']
                                })

        json_rep = {
            'id': space.id,
            'spot_id': spot.get('id', None),
            'is_published': True if space.spot_id is not None else False,
            'is_modified': True if space.pending is not None else False,
            'name': spot.get('name', ''),
            'type': spot.get('type', ''),
            'location': spot.get('location', ''),
            'manager': spot.get('manager', ''),
            'editors': spot.get('editors', []),
            'modified_by': spot.get('modified_by', None),
            'last_modified': spot.get('last_modified', None),
            'missing_sections': missing_sections
        }

        if settings.SS_SPACE_DESCRIPTION:
            json_rep['description'] = self._spot_value(spot, settings.SS_SPACE_DESCRIPTION)

        return json_rep

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

    def _spot_value(self, spot, key):
        return self._spacemap.get_value_by_keylist(spot, key.split('.'))


class SpaceImage(RESTDispatch):
    def GET(self, args, **kwargs):

        # Required settings for the client
        consumer, client = oauth_initialization()

        url = "{0}/api/v1/spot/{1}/image/{2}".format(settings.SS_WEB_SERVER_HOST,
                                                     kwargs['space_id'], kwargs['image_id'])

        resp, content = client.request(url, 'GET')

        if resp.status != 200:
            return self.error_response(resp.status_code, msg="Error loading image")

        return self.json_response(content)
