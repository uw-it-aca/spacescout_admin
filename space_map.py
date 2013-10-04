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
from spacescout_admin.models import *
import simplejson as json
import copy


class SpaceMapException(Exception): pass


class SpaceMap(object):
    """Builds a Space representation, layering Space modifications over a new or existing Spot
    """
    def space_rep(self, space, spot, schema):
        json_rep = space.json_data_structure()

        # overlay a spot copy with modifications
        if space.pending and len(space.pending) > 0:
            spot = copy.deepcopy(spot)
            pending = json.loads(space.pending)
            for p in pending:
                self.set_by_key(p, pending.get(p), spot)

            if not json_rep.get('is_complete') and '_missing_fields' in pending:
                json_rep['missing_fields'] = pending.get('_missing_fields')


        json_rep['is_published'] = (space.spot_id is not None)
        json_rep['is_modified'] = (space.pending and len(space.pending) != 0)
        json_rep['name'] = spot.get('name', '')
        json_rep['type'] = spot.get('type', '')
        json_rep['manager'] = spot.get('manager', space.manager)
        json_rep['editors'] = spot.get('editors', [])
        json_rep['modified_by'] = space.modified_by
        json_rep['last_modified'] = spot.get('last_modified', space.modified_date)
        json_rep['group'] = spot.get('location').get('building_name')
        json_rep['sections'] = []

        if settings.SS_SPACE_DESCRIPTION:
            json_rep['description'] = self.get_value(settings.SS_SPACE_DESCRIPTION, spot, schema)

        for secdef in settings.SS_SPACE_DEFINITIONS:
            section = {
                'section': secdef['section']
            }

            if secdef['section'] == 'hours_access':
                hours = spot['available_hours']
                section['available_hours'] = []
                # present all 7 days so translation and order happen here
                for d in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                    hrs = {
                        'day': d
                    }

                    if d in hours:
                        hrs['hours'] = hours[d]
        
                    section['available_hours'].append(hrs)
            elif secdef['section'] == 'images':
                section['images'] = [];
                if space.spot_id:
                    for img in spot['images']:
                        section['images'].append({
                            'description': img.get('description'),
                            'url': "{0}api/v1/space/{1}/image/-{2}".format(settings.APP_URL_ROOT, space.id, img.get('id'))
                        })
                try:
                    for img in SpaceImage.objects.filter(space=space):
                        section['images'].append({
                            'description': img.description,
                            'url': "{0}/api/v1/space/{1}/image/{2}".format(settings.APP_URL_ROOT, space.id, img.id)
                        })

                except SpaceImage.DoesNotExist:
                    pass

            if 'fields' in secdef:
                section['fields'] = []
        
                for f in secdef['fields']:
                    field = {
                        'name': f.get('name', '')
                    }

                    if 'required' in f:
                        field['required'] = f['required']
        
                    if 'help' in f:
                        field['help'] = f['help']
        
                    if 'value' in f:
                        if isinstance(f['value'], dict):
                            value = copy.deepcopy(f['value'])
                            value['value'] = self.get_value(value['key'], spot, schema)
                        else:
                            vals = []
                            for v in f['value']:
                                vc = copy.deepcopy(v)
                                vc['value'] = self.get_value(v['key'], spot, schema)
                                vals.append(vc)
        
                            value = vals
        
                        if value:
                            field['value'] = value
        
                    section['fields'].append(field)
        
            json_rep['sections'].append(section)

        return json_rep

    def pending_spot(self, space, schema):
        spot = self._init_spot(schema)

        # overlay a spot copy with modifications
        if space.pending and len(space.pending) > 0:
            spot = copy.deepcopy(spot)
            pending = json.loads(space.pending)
            for p in pending:
                self.set_by_key(p, pending.get(p), spot)

        spot['is_published'] = False
        spot['is_modified'] = True
        spot['last_modified'] = space.modified_date.isoformat() if space.modified_date else None
        spot['modified_by'] = space.modified_by
        return spot

    def _init_spot(self, data_src):
        data = copy.deepcopy(data_src)
        for k in data:
            if isinstance(data[k], list):
                if data[k][0] == 'true':
                    data[k] = None
                else:
                    data[k] = []
            elif isinstance(data[k], dict):
                data[k] = self._init_spot(data[k])
            else:
                data[k] = ''
                
        return data

    def get_value(self, key, src_dict, schema):
        kl = key.split('.')
        v = self.get_by_keylist(kl, src_dict)
        tv = self.get_by_keylist(kl, schema)
        if isinstance(tv, list) and len(tv) == 1 and tv[0].lower() == 'true':
            v = True if v or (isinstance(v, str) and v.lower() == 'true') else False

        return v

    def get_by_keylist(self, kl, d):
        try:
            v = d[kl[0]]
            return v if len(kl) == 1 else self.get_by_keylist(kl[1:], v)
        except KeyError:
            return None

    def set_by_key(self, k, v, d):
        s = k.split('.')
        if len(s) > 1:
            if s[0] in d:
                return self.set_by_key('.'.join(s[1:]), v, d[s[0]])
        else:
            if k in d:
                d[k] = v
