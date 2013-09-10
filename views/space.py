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
from django.utils.translation import ugettext as _
from django.http import Http404
from django.http import HttpResponse
import simplejson
import re
from spacescout_admin.oauth import oauth_initialization


def SpaceView(request, space_id):

    # Required settings for the client
    consumer, client = oauth_initialization()

    url = "{0}/api/v1/schema".format(settings.SS_WEB_SERVER_HOST)
    resp, content = client.request(url, 'GET')
    if resp.status == 200:
        schema = simplejson.loads(content)
    else:
        response = HttpResponse("Error loading schema")
        response.status_code = resp.status_code
        return response

    url = "{0}/api/v1/spot/{1}".format(settings.SS_WEB_SERVER_HOST, space_id)
    resp, content = client.request(url, 'GET')
    if resp.status == 404:
        url = request.get_host()
        url = url + "/contact"
        raise Http404
    elif resp.status != 200:
        response = HttpResponse("Error loading spot")
        response.status_code = resp.status_code
        return response

#    f1 = open('/tmp/spot.log', 'a+')
#    f1.write('SPOT: %s\n' % content)
#    f1.close()

    params = simplejson.loads(content)

    #
    # FILTER: params["manager"] == REMOTE_USER
    #

    
    modified_date = params["last_modified"][5:10] + '-' + params["last_modified"][:4]
    params["last_modified"] = re.sub('-', '/', modified_date)

    space = {
        'name': params['name'],
        'type': params['type'],
        'manager': params['manager'],
        'editors': params['editors'] if 'editors' in params else [],
        'sections': []
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
                    
                if d in params['available_hours']:
                    hrs['hours'] = params['available_hours'][d]

                section['available_hours'].append(hrs)

        elif secdef['section'] == 'images':
            section['thumbnails'] = [];
            section['images'] = params['images']
            for j in params['images']:
                section['thumbnails'].append({
                        'img_url': j['url'],
                        'caption': j['description']
                })

        if 'fields' in secdef:
            section['fields'] = []

            for f in secdef['fields']:
                field = {
                    'name': f['name'] if 'name' in f else ''
                }

                if 'required' in f:
                    field['required'] = f['required']

                if 'help' in f:
                    field['help'] = f['help']

                if 'value' in f:
                    if isinstance(f['value'], dict):
                        value = value_from_key(params, f['value'], schema)
                    else:
                        vals = []
                        for v in f['value']:
                            vals.append(value_from_key(params, v, schema))

                        value = vals

                    if value:
                        field['value'] = value

                section['fields'].append(field)

        space['sections'].append(section)

    content = simplejson.dumps(space)

    return HttpResponse(content, mimetype='application/json')


def value_from_key(d, v, s):
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
        val = value_from_keylist(d, k)

        if type_from_keylist(s, k) == 'boolean':
            val = True if val or (isinstance(val, str) and val.lower() == 'true') else False

        val_obj['value'] = val

    return val_obj


def value_from_keylist(d, klist):
    try:
        val = d[klist[0]]
        return val if len(klist) == 1 else value_from_keylist(val, klist[1:])
    except KeyError:
        return None


def type_from_keylist(schema, klist):
    t = value_from_keylist(schema, klist)
    if isinstance(t, list):
        return 'boolean' if len(t) == 1 and t[0].lower() == 'true' else list

    return t
