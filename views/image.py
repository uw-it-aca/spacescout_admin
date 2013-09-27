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

    Changes
    =================================================================

    sbutler1@illinois.edu: adapt to the new RESTDispatch framework.
"""

from django.conf import settings
from django.http import HttpResponse
from django.utils.http import http_date
from django.core.servers.basehttp import FileWrapper
from django.core.exceptions import ValidationError
from spacescout_admin.models import *
from spacescout_admin.rest_dispatch import RESTDispatch
from spacescout_admin.oauth import oauth_initialization


class SpaceImage(RESTDispatch):
    """ Handles actions at /api/v1/space/<space id>/image/<image id>.
    GET returns 200 with the image.
    PUT returns 200 and updates the image.
    DELETE returns 200 and deletes the image.
    """
    def GET(self, request, space_id, image_id):

        try:
            space = Space.objects.get(id=space_id)

            if image_id[:1] == '-':
                return self._spot_image(space.spot_id, image_id[1:])

            img = SpaceImage.objects.get(pk=image_id)
            space = img.space

            if int(space.pk) != int(space_id):
                raise Space.DoesNotExist()

            response = HttpResponse(FileWrapper(img.image))

            # 7 day timeout?
            response['Expires'] = http_date(time.time() + 60 * 60 * 24 * 7)
            response["Content-length"] = img.image.size
            response["Content-type"] = img.content_type
            return response

        except Space.DoesNotExist:
            if e.args[0]['status_code'] == 404:
                self.error404_response()  # no return

    def _spot_image(self, spot_id, image_id):
        # Required settings for the client
        consumer, client = oauth_initialization()

        url = "{0}/api/v1/spot/{1}/image/{2}".format(settings.SS_WEB_SERVER_HOST,
                                                     spot_id, image_id)

        resp, content = client.request(url, 'GET')

        if resp.status != 200:
            return self.error_response(resp.status_code, msg="Error loading image")

        return self.json_response(content)

    def PUT(self, request, space_id, image_id):
        img = SpaceImage.objects.get(pk=image_id)
        space = img.space

        if int(space.pk) != int(space_id):
            self.error404_response()

        # This trick was taken from piston
        request.method = "POST"
        request._load_post_and_files()
        request.method = "PUT"

        if "image" in request.FILES:
            img.image = request.FILES["image"]
        if "description" in request.POST:
            img.description = request.POST["description"]
        img.save()

        return self.GET(request, space_id, image_id)

    def DELETE(self, request, space_id, image_id):
        img = SpaceImage.objects.get(pk=image_id)
        space = img.space

        if int(space.pk) != int(space_id):
            self.error404_response()

        img.delete()

        return HttpResponse(status=200)
