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
from spacescout_admin.oauth import oauth_initialization


class SpotException(Exception): pass


class Spot(object):
    """CRUD operations on spots
    """
    def get(self, spot_id):
        consumer, client = oauth_initialization()

        url = "{0}/api/v1/spot/{1}".format(settings.SS_WEB_SERVER_HOST, spot_id)
        resp, content = client.request(url, 'GET')

        if resp.status == 200:
            return json.loads(content)

        raise SpotException({'status_code': resp.status,
                             'status_text': "Error loading schema"})

    def put(self, spot):
        raise SpotException({'status_code': 500,
                             'status_text': "PUT not implemented"})

    def post(self, spot):
        raise SpotException({'status_code': 500,
                             'status_text': "POST not implemented"})

