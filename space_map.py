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
import simplejson as json
import copy


class SpaceMapException(Exception): pass


class SpaceMap(object):
    """Layers Spaces over Spots
    """
    def space_representation(self, space, spot, schema):
        json_rep = {
            'id': space.id,
            'spot_id': space.spot_id,
            'is_published': True if (space.spot_id is not None) else False,
            'is_modified': True if (space.pending is not None) else False,
            'name': spot.get('name', ''),
            'type': spot.get('type', ''),
            'manager': spot.get('manager', space.manager),
            'editors': spot.get('editors', []),
            'modified_by': space.modified_by,
            'last_modified': spot.get('last_modified', space.modified_date),
            'sections': [],
            'pending': space.pending
        }

        for secdef in settings.SS_SPACE_DEFINITIONS:
            section = {
                'section': secdef['section']
            }

            if secdef['section'] == 'hours':
                section['available_hours'] = []
                # present all 7 days so translation and order happen here
                for d in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                    hrs = {
                        'day': d
                    }

                    if d in spot['available_hours']:
                        hrs['hours'] = spot['available_hours'][d]
        
                    section['available_hours'].append(hrs)
            elif secdef['section'] == 'images':
                section['thumbnails'] = [];
                section['images'] = spot['images']
                for j in spot['images']:
                    section['thumbnails'].append({
                                                      'img_url': j['url'].replace('/spot/', '/space/') if 'url' in j else '',
                                                      'caption': j['description'] if 'description' in j else ''
                                                 })

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
                            value = self.get_value_by_key(spot, f['value'], schema)
                        else:
                            vals = []
                            for v in f['value']:
                                vals.append(self.get_value_by_key(spot, v, schema))
        
                            value = vals
        
                        if value:
                            field['value'] = value
        
                    section['fields'].append(field)
        
            json_rep['sections'].append(section)

        return json_rep

    def pending_spot(self, space, schema):
        spot = self._init_spot(schema)
        spot['is_published'] = False
        spot['is_modified'] = True
        spot['last_modified'] = space.modified_date.isoformat()
        spot['modified_by'] = space.modified_by
        spot['available_hours'] = {}
        if space.pending:
            j = json.loads(space.pending)
            for p in j:
                self.set_value_by_key(spot, p, j[p])

        return spot

    def _init_spot(self, data_src):
        data = copy.deepcopy(data_src)
        for k in data:
            if isinstance(data[k], list):
                if data[k][0] == 'true':
                    data[k] = None
                elif isinstance(data[k][0], dict):
                    data[k] = []
                else:
                    data[k] = [data[k][0]]
            elif isinstance(data[k], dict):
                data[k] = self._init_spot(data[k])
            else:
                data[k] = ''
                
        return data

    def get_value_by_key(self, d, v, s):
        val_obj = None

        if 'key' in v:
            val_obj = {
                'key': v['key']
            }
    
            if 'edit' in v:
                val_obj['edit'] = v['edit']
    
            if 'format' in v:
                val_obj['format'] = v['format']
    
            if 'map' in v:
                val_obj['map'] = v['map']
    
            k = v['key'].split('.')
            val = self.get_value_by_keylist(d, k)
    
            if self.type_from_keylist(s, k) == 'boolean':
                val = True if val or (isinstance(val, str) and val.lower() == 'true') else False
    
            val_obj['value'] = val
    
        return val_obj

    def get_value_by_keylist(self, d, klist):
        try:
            val = d[klist[0]]
            return val if len(klist) == 1 else self.get_value_by_keylist(val, klist[1:])
        except KeyError:
            return None

    def type_from_keylist(self, schema, klist):
        t = self.get_value_by_keylist(schema, klist)
        if isinstance(t, list):
            return 'boolean' if len(t) == 1 and t[0].lower() == 'true' else list
    
        return t

    def set_value_by_key(self, d, k, v):
        s = k.split('.')
        if len(s) > 1:
            if s[0] in d:
                return self.set_value_by_key(d[s[0]], '.'.join(s[1:]), v)
        else:
            if k in d:
                d[k] = v
