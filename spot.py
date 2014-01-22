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
from poster.streaminghttp import register_openers
from poster.encode import multipart_encode
import urllib2
import time
import re
from spacescout_admin.oauth import oauth_initialization, oauth_nonce


class SpotException(Exception): pass


class SpotAccess(object):
    """CRUD operations on spots/images
    """
    def _pull(self, method, spot_url):
        consumer, client = oauth_initialization()

        resp, content = client.request(spot_url, 'GET')

        if resp.status == 200:
            return json.loads(content) if resp.get('content-type').lower() == 'application/json' else content

        raise SpotException({'status_code': resp.status,
                             'status_text': "Error loading spot"})

    def _push(self, method, spot_url, spot, user):
        consumer, client = oauth_initialization()

        headers = {
            "XOAUTH_USER": "%s" % user,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        if 'etag' in spot and len(spot.get('etag')):
            headers['If-Match'] = spot.get('etag')

        resp, content = client.request(spot_url,
                                       method=method,
                                       body=json.dumps(spot),
                                       headers=headers)

        if resp.status == 200 or resp.status == 201:
            return resp, json.loads(content) if content else {}

        raise Exception("Unable to {0} spot: Server response {1}".format(method, resp.status))


class Spot(SpotAccess):
    """CRUD operations on spots
    """
    def get(self, spot_id):
        return self._pull("GET", self._service_url(spot_id))

    def put(self, spot, user):
        self._push("PUT", self._service_url(spot.get('id')), spot, user)

    def post(self, spot, user):
        resp, content = self._push("POST", self._service_url(), spot, user)
        return self._pull("GET", resp.get('location'))

    def delete(self, spot_id):
        return self._pull("DELETE", self._service_url(spot_id))

    def _service_url(self, spot_id=None):
        return "{0}/api/v1/spot{1}".format(settings.SS_WEB_SERVER_HOST,
                                            ''.join(['/', str(spot_id)]) if spot_id else '')


class Image(SpotAccess):
    """CRUD operations on images
    """
    def __init__(self, spot_id):
        self._spot_id = spot_id

    def get(self, image_id):
        return self._pull("GET", self._service_url(image_id))

    def put(self, image, user):
        self._push("PUT", self._service_url(image.get('id')), image, user)

    def post(self, image_path, description, user):
        consumer, client = oauth_initialization()
        resp, content = client.request("{0}/api/v1/spot".format(settings.SS_WEB_SERVER_HOST), 'GET')
        i = resp['content-location'].find('oauth_signature=')
        i += len('oauth_signature=')
        signature = resp['content-location'][i:]

        authorization = 'OAuth oauth_version="1.0",oauth_nonce="%s",oauth_timestamp="%d",oauth_consumer_key="%s",oauth_signature_method="HMAC-SHA1",oauth_signature="%s"' % (oauth_nonce(), int(time.time()), settings.SS_WEB_OAUTH_KEY, signature)

        register_openers()

        f = open(image_path, mode='rb')

        datagen, headers = multipart_encode({
            'description': description,
            'image': f
        })

        headers["XOAUTH_USER"] = "%s" % user
        headers["Authorization"] = authorization
        req = urllib2.Request(self._service_url(), datagen, headers)
        try:
            response = urllib2.urlopen(req)
        except (urllib2.URLError, urllib2.HTTPError) as e:
            raise SpotException({'status_code': e.code,
                                 'status_text': e.args})

        f.close()

        return { 'id': re.match(r'.*/(\d+)$', response.info().get('Location')).group(1) }

    def delete(self, image_id):
        return self._pull("DELETE", self._service_url(image_id))

    def _service_url(self, image_id=None):
        return "{0}/api/v1/spot/{1}/image{2}".format(settings.SS_WEB_SERVER_HOST,
                                                      self._spot_id, ''.join(['/', str(image_id)]) if image_id else '')
