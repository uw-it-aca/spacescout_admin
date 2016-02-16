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
from django.core.mail import send_mail
from spacescout_admin.models import *
from spacescout_admin.spot import Spot, Image, SpotException
from spacescout_admin.space_map import SpaceMap, SpaceMapException
from spacescout_admin.rest_dispatch import RESTDispatch
from spacescout_admin.oauth import oauth_initialization
from spacescout_admin.fields import space_definitions, space_creation_fields
from spacescout_admin.permitted import Permitted, PermittedException
from spacescout_admin.views.schema import SpotSchema, SpotSchemaException
import simplejson as json
import logging
import math

logger = logging.getLogger(__name__)

class SpaceManager(RESTDispatch):
    """ Performs actions on Space models at api/v1/space/(?P<space_id>\d+)/
        Space models are a layer on top of spotseeker_server Spot models.
        GET returns requested Space model(s)
        PUT modifies a Space model, conditionally modifies the Spot model supporting it
        POST creates a Space model
    """
    def __init__(self):
        self._spacemap = SpaceMap()

    def GET(self, args, **kwargs):
        if 'space_id' in kwargs:
            return self._space_detail(kwargs['space_id'])

        return self._space_list()

    def PUT(self, args, **kwargs):
        try:
            schema = SpotSchema().get()
            space_id = kwargs['space_id']
            space = Space.objects.get(id=space_id)
            if space.is_deleted:
                self.error404_response()

            if space.spot_id:
                spot = Spot().get(space.spot_id)
            else:
                spot = self._spacemap.pending_spot(space, schema)

            Permitted().can_edit(self._request.user, space, spot)

            data = json.loads(self._request.read())

            for field in data:
                if field and field.startswith("extended_info.has_"):
                    data[field] = data[field].lower()
            fields, missing_fields = self._validate(spot, data)

            pending = json.loads(space.pending) if space.pending else {}

            for field in fields:
                if field == 'editors':
                    try:
                        for editor in SpaceEditor.objects.filter(space=space):
                            editor.delete()
                    except SpaceEditor.DoesNotExist:
                        pass

                    for username in fields[field].split(','):
                        editor = username.strip()
                        if len(editor):
                            space_editor = SpaceEditor(editor=username.strip(),space=space)
                            space_editor.save()
                else:
                    pending[field] = fields[field]

                pending[field] = fields[field]

            if len(missing_fields) > 0:
                space.is_complete = None
                space.is_pending_publication = None
                pending['_missing_fields'] = missing_fields
            else:
                space.is_complete = True

            # SPOT-1303
            if 'manager' in data:
                space.manager = data['manager']

            if 'is_published' in data:
                if data.get('is_published') == True:
                    space_images = SpaceImage.objects.filter(space=space.id)
                    image_links = SpotImageLink.objects.filter(space=space.id,
                                                              is_deleted__isnull=False)
                    if space.is_complete and (space.pending and len(space.pending) != 0
                                              or len(space_images) or len(image_links)):

                        # create/update modified spot
                        spot = self._spacemap.apply_pending(spot, space)

                        if space.spot_id:
                            Spot().put(spot, self._request.user)
                        else:
                            spot = Spot().post(spot, self._request.user)
                            space.spot_id = spot.get('id')

                        # fix up images, adding new, updating spot images
                        for img in image_links:
                            if img.is_deleted:
                                Image(space.spot_id).delete(img.image_id)
                                img.delete()
                            else:
                                Image(space.spot_id).put(img.image_id,
                                                         { 'display_index' : img.display_index },
                                                         self._request.user)

                        for img in space_images:
                            spotimage = Image(space.spot_id).post(img.image.path,
                                                                  img.description,
                                                                  self._request.user)
                            link = SpotImageLink(space=space,
                                                 spot_id=space.spot_id,
                                                 image_id=spotimage.get('id'),
                                                 display_index=img.display_index)
                            link.save()
                            img.delete()

                    pending = {}
                    space.is_complete = None
                    space.is_pending_publication = None
                else: # unpublish
                    # pull spot data into space.pending
                    # remove spot from spot server
                    # spot().delete(spot.id)
                    # images?
                    pass
                    
            elif 'is_pending_publication' in data:
                if data.get('is_pending_publication') == True:
                    if space.is_pending_publication != True:
                        space.is_pending_publication = True
                        if hasattr(settings, 'SS_PUBLISHER_EMAIL'):
                            send_mail('Space Publishing Request',
                                      'A request has been made to publish space\n\t http%s://%s%sspace/%s/' \
                                          % ('s' if self._request.is_secure() else '',
                                             self._request.get_host(),
                                             settings.APP_URL_ROOT,
                                             space.id),
                                      settings.SS_PUBLISHER_FROM,
                                      settings.SS_PUBLISHER_EMAIL,
                                      fail_silently=False)
            else:
                space.is_pending_publication = False

            space.modified_by = self._request.user.username
            space.pending = json.dumps(pending) if len(pending) > 0 else None
            space.save()
            return self.json_response('{"id": "%s"}' % space.id)
        except PermittedException:
            return self.error_response(401, "Unauthorized")
        except Space.DoesNotExist:
            if e.args[0]['status_code'] == 404:
                self.error404_response()
                # no return
        except (SpaceMapException, SpotException, SpotSchemaException) as e:
            return self.error_response(e.args[0]['status_code'],
                                       e.args[0]['status_text'])
        except Exception as ex:
            return self.error_response(400, "Unknown error: %s" % ex)

    def POST(self, args, **kwargs):
        try:
            Permitted().can_create(self._request.user)
            schema = SpotSchema().get()
            space = Space(manager=self._request.user,
                          modified_by=self._request.user)
            spot = self._spacemap.pending_spot(space, schema)

            data = json.loads(self._request.read())

            fields, missing_fields = self._validate(spot, data)
            pending = {}
            for field in fields:
                if field == 'editors':
                    for username in fields[field].split(','):
                        editor = username.strip()
                        if len(editor):
                            space_editor = SpaceEditor(editor=username.strip(),space=space)
                            space_editor.save()
                else:
                    pending[field] = fields[field]

            if len(missing_fields) > 0:
                space.is_complete = None
                pending['_missing_fields'] = missing_fields
            else:
                space.is_complete = True

            for field in space_creation_fields():
                if 'value' in field and 'key' in field['value']:
                    key = field['value']['key']
                    if 'required' in field and (key not in data or bool(data[key]) == False):
                        return self.error_response(400, "Bad Request")

            space.pending = json.dumps(pending) if len(pending) > 0 else None


            space.save()
            return self.json_response('{"id": "%s"}' % space.id)
        except PermittedException:
            return self.error_response(401, "Unauthorized")

    def DELETE(self, args, **kwargs):
        try:
            space_id = kwargs['space_id']
            schema = SpotSchema().get()
            space = Space.objects.get(id=space_id)
            if space.is_deleted:
                raise Space.DoesNotExist

            if space.spot_id:
                spot = Spot().get(space.spot_id)
            else:
                spot = self._spacemap.pending_spot(space, schema)

            Permitted().can_edit(self._request.user, space, spot)
            space.is_deleted = True
            space.save()
            return self.json_response(json.dumps('{}'))
        except Space.DoesNotExist:
            self.error404_response()

    def _validate(self, spot, data):
        fields = {}
        missing_fields = []
        seen_fields = {}
        for section in space_definitions():
            for field in section['fields'] if 'fields' in section else []:
                for value in field['value'] if isinstance(field['value'], list) else [field['value']]:
                    key = value['key']
                    val = data[key] if key in data else None
                    orig_val = self._spot_value(key, spot)
                    if key in data and val != orig_val:
                        fields[key] = val
                        # SPOT-1277
                        if val == None or val == "":
                            orig_val = None

                    if 'required' in field and bool(val) == False and bool(orig_val) == False:
                        s = section.get('section')
                        f = field.get('name')
                        if s + f not in seen_fields:
                            missing_fields.append({ 'section': s, 'field': f })
                            seen_fields[s + f] = True

        if 'available_hours' in data:
            valid_hours = True
            available = {}
            for d in data['available_hours']:
                hours = [0 for i in range(0,2400)]
                for h in data['available_hours'][d]:
                    if len(h) == 2:
                        opn = int("".join(h[0].split(":")))
                        cls = int("".join(h[1].split(":")))
                        if opn < 0 or opn > 2359 or opn % 100 >= 60 or cls < 0 or cls > 2359 or cls % 100 >= 60 or opn >= cls:
                            valid_hours = False
                        else:
                            for i in range(opn, cls):
                                if i % 100 < 60:
                                    hours[i] = 1
                    else:
                        valid_hours = False

                available[d] = []
                opn = 0
                state = 0
                for i in range(0, 2360):
                    if i % 100 < 60:
                        if state != hours[i]:
                            state = hours[i]
                            if hours[i]:
                                opn = i
                            else:
                                available[d].append(self._hours_range([opn, i]))

            if valid_hours:
                fields['available_hours'] = available

        return fields, missing_fields

    def _hours_range(self, hours):
        r = []
        for i in range(0, 2):
            r.append(":".join([self._double_digit(math.trunc(hours[i]/100)),
                               self._double_digit(hours[i]%100)]))

        return r

    def _double_digit(self, d):
        return "{0}{1}".format('0' if d < 10 else '', d)

    def _space_detail(self, space_id):
        try:
            schema = SpotSchema().get()
            space_model = Space.objects.get(id=space_id)
            if space_model.is_deleted:
                raise Space.DoesNotExist

            if space_model.spot_id:
                spot = Spot().get(space_model.spot_id)
            else:
                spot = self._spacemap.pending_spot(space_model, schema)

            Permitted().can_edit(self._request.user, space_model, spot)

            return self.json_response(json.dumps(self._spacemap.space_rep(space_model, spot, schema)))

        except PermittedException:
            return self.error_response(401, "Unauthorized")
        except Space.DoesNotExist:
            self.error404_response()
        except (SpaceMapException, SpotException, SpotSchemaException) as e:
            return self.error_response(e.args[0]['status_code'],
                                       e.args[0]['status_text'])

    def _space_list(self):
        filter = {}
        published = True
        complete = True
        json_rep = []
        seen = {}
        permitted = Permitted()

        try:
            is_admin = permitted.is_admin(self._request.user)
        except PermittedException:
            is_admin = False

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
                        if space.is_deleted:
                            continue
                    except Space.DoesNotExist:
                        space = Space(spot_id=spot_id,
                                      manager=spot.get('manager'),
                                      is_complete=True)
                        space.save()

                    if not is_admin:
                        permitted.can_edit(self._request.user, space, spot)

                    if str(spot_id) not in seen:
                        seen[str(spot_id)] = 1
                        json_rep.append(self._spacemap.space_rep(space, spot, schema))

                except PermittedException:
                    pass
                except SpaceMapException as e:
                    return self.error_response(e.args[0]['status_code'],
                                               e.args[0]['status_text'])

        for space in Space.objects.filter(**filter):
            if space.is_deleted or str(space.spot_id) in seen:
                continue

            try:
                if space.spot_id:
                    try:
                        spot = Spot().get(space.spot_id)
                    except SpotException as se:
                        logger.info("No Spot for %s.  Error: %s" % (space.spot_id, se.args[0]))
                        continue
                else:
                    spot = self._spacemap.pending_spot(space, schema)

                if not is_admin:
                    permitted.can_edit(self._request.user, space, spot)

                json_rep.append(self._spacemap.space_rep(space, spot, schema))
            except PermittedException:
                pass
            except SpaceMapException as e:
                return self.error_response(e.args[0]['status_code'],
                                           e.args[0]['status_text'])

        return self.json_response(json.dumps(json_rep))

    def _spot_value(self, key, spot):
        return self._spacemap.get_by_keylist(key.split('.'), spot)

    def _get_spots(self, search_args):
        consumer, client = oauth_initialization()

        #for key in options:
        #    if isinstance(options[key], types.ListType):
        #        for item in options[key]:
        #            args.append("{0}={1}".format(urllib.quote(key), urllib.quote(item)))
        #    else:
        #        args.append("{0}={1}".format(urllib.quote(key), urllib.quote(options[key])))

        #url = "{0}/api/v1/spot/search?{1}".format(settings.SS_WEB_SERVER_HOST, "&".join(search_args))
        url = "{0}/api/v1/spot/all".format(settings.SS_WEB_SERVER_HOST)

        resp, content = client.request(url, 'GET')

        if resp.status != 200:
            raise Exception("Unable to load spots")

        i18n_json = []
        for spot in json.loads(content):
            string_val = ''
            for x in range(0, len(spot['type'])):
                if x is 0:
                    string_val = _(spot['type'][x])
                else:
                    string_val = string_val + ', ' + _(spot['type'][x])

                spot['type'] = string_val
                i18n_json.append(spot)

        return i18n_json
