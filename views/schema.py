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
from django.http import Http404
from django.http import HttpResponse
import simplejson as json
from spacescout_admin.oauth import oauth_initialization


class SpotSchemaException(Exception): pass


class SpotSchema():
    def get(self):
        # Required settings for the client
        consumer, client = oauth_initialization()

        url = "{0}/api/v1/schema".format(settings.SS_WEB_SERVER_HOST)
        resp, content = client.request(url, 'GET')
        if resp.status == 200:
            schema = json.loads(content)
        else:
            raise SpotSchemaException({
                    'status_code': resp.status,
                    'status_text': "Error loading schema"
                    })

        return schema


@login_required
def SchemaView(request):

    try:
        schema = SpotSchema().get()
    except SpotSchemaException as e:
        if e.args[0]['status'] == 404:
            url = request.get_host()
            url = url + "/contact"
            raise Http404
        elif e.args[0]['status'] != 200:
            response = HttpResponse("Error loading spot")
            response.status_code = e.args[0]['status_code']
            return response

    return HttpResponse(json.dumps(schema), mimetype='application/json')
