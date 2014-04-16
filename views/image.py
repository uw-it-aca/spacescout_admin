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

"""

from django.conf import settings
from django.http import HttpResponse
from django.utils.http import http_date
from django.core.servers.basehttp import FileWrapper
from spacescout_admin.models import *
from spacescout_admin.rest_dispatch import RESTDispatch
from spacescout_admin.oauth import oauth_initialization
from spacescout_admin.permitted import Permitted, PermittedException
import simplejson as json
import time


class SpaceImageManager(RESTDispatch):
    """ Handles actions at /api/v1/space/<space id>/image/<image id>.
    GET returns 200 with the image.
    PUT returns 200 and updates the image.
    DELETE returns 200 and deletes the image.
    """
    def GET(self, request, space_id, image_id):

        try:
            space = Space.objects.get(id=space_id)

            if image_id[0] == '-':
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
        try:
            link = SpotImageLink.objects.get(id=image_id)
        except:
            self.error404_response()  # no return

        # Required settings for the client
        consumer, client = oauth_initialization()
        url = "{0}/api/v1/spot/{1}/image/{2}".format(settings.SS_WEB_SERVER_HOST,
                                                     spot_id, link.image_id)

        resp, content = client.request(url, 'GET')

        if resp.status != 200:
            return self.error_response(resp.status, msg="Error loading image")

        return self.json_response(content)

    def PUT(self, request, space_id, image_id):
        try:
            if image_id[0] == '-':
                img = SpotImageLink.objects.get(id=image_id[1:])
                links = SpotImageLink.objects.filter(space=space_id).exclude(id=img.id)
                imgs = SpaceImage.objects.filter(space=space_id)
            else:
                img = SpaceImage.objects.get(pk=image_id)
                imgs = SpaceImage.objects.filter(space=space_id).exclude(id=img.id)
                links = SpotImageLink.objects.filter(space=space_id)
                space = img.space

                if int(space.pk) != int(space_id):
                    raise SpaceImage.DoesNotExist()

                space = Space.objects.get(id=space_id)
                Permitted().can_edit(request.user, space, {})

        except PermittedException:
            return self.error_response(401, "Unauthorized")
        except (Space.DoesNotExist, SpaceImage.DoesNotExist):
            if e.args[0]['status_code'] == 404:
                self.error404_response()  # no return

        body = json.loads(request.body)

        if "display_index" in body:
            img.display_index = body["display_index"]
            for n in range(len(links) + len(imgs)):
                for l in links:
                    if l.display_index >= img.display_index:
                        l.display_index += 1
                        l.save()

                for i in imgs:
                    if i.display_index >= img.display_index:
                        i.display_index += 1
                        i.save()

        if "description" in body and 'description' in img:
            img.description = body["description"]

        img.save()

        return self.json_response(json.dumps({ 'id': img.id }))

    def POST(self, request, space_id):
        try:
            space = Space.objects.get(id=space_id)
            Permitted().can_edit(request.user, space, {})
            links = SpotImageLink.objects.filter(space=space_id)
            imgs = SpaceImage.objects.filter(space=space_id)
        except PermittedException:
            return self.error_response(401, "Unauthorized")
        except Space.DoesNotExist:
            self.error404_response()  # no return

        img = SpaceImage(
            description="",
            space=space,
            display_index=len(links) + len(imgs),
            upload_user=request.user,
            upload_application="admin"
        )

        if "image" in request.FILES:
            img.image = request.FILES["image"]
        if "description" in request.POST:
            img.description = request.POST["description"]

        img.save()

        return self.json_response(json.dumps({ 'id': img.id }))

    def DELETE(self, request, space_id, image_id):
        try:
            if image_id[0] == '-':
                link = SpotImageLink.objects.get(id=image_id[1:])
                link.is_deleted = True
                link.save()
            else:
                img = SpaceImage.objects.get(pk=image_id)
                space = img.space
                Permitted().can_edit(request.user, space, {})
                if int(space.pk) != int(space_id):
                    raise SpaceImage.DoesNotExist()

                space = Space.objects.get(id=space_id)
                img.delete()
        except PermittedException:
            return self.error_response(401, "Unauthorized")
            self.error404_response()  # no return
        except (Space.DoesNotExist, SpaceImage.DoesNotExist, SpotImageLink.DoesNotExist):
            self.error404_response()  # no return


        return HttpResponse(status=200)
