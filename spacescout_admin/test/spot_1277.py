""" Copyright 2014 UW Information Technology, University of Washington

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

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.test.utils import override_settings
from django.test.client import Client
from spacescout_admin.models import Space
import json

@override_settings(SS_ADMIN_FIELDS_MODULE='spacescout_admin.field_definitions.default')
@override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
class Spot1277(TestCase):
    def setUp(self):
        admins, created = Group.objects.get_or_create(name="spacescout_admins")
        user = User.objects.create_user("test_user", "test@example.com", "ok")

        admins.user_set.add(user)

        self.client = Client()
        self.client.login(username="test_user", password="ok")

        response = self.client.post("/api/v1/space/", '{ "name": "test_space", "manager": "javerage" }', content_type="application/json")

        data = json.loads(response.content)
        self.space_id = data['id']
        self.url = "/api/v1/space/%s/" % data['id']


    """ Test to make sure we unpublish spots with incomplete data """
    def test_puts(self):

        response = self.client.put(self.url, '{"name":"SPOT-1277","manager":"javerage","editors":""}', content_type="application/json")
        data = json.loads(response.content)


        response = self.client.get("/api/v1/space/?complete=0&published=0")
        self.assertEqual(self._has_space_in_response(response), True)

        response = self.client.get("/api/v1/space/?complete=1&published=0")
        self.assertEqual(self._has_space_in_response(response), False)

        response = self.client.get("/api/v1/space/?complete=1")
        self.assertEqual(self._has_space_in_response(response), False)

        response = self.client.put(self.url, '{"location.latitude":"47.651952","location.longitude":"-122.303141","extended_info.campus":"seattle"}', content_type="application/json")

        response = self.client.get("/api/v1/space/?complete=0&published=0")
        self.assertEqual(self._has_space_in_response(response), False)

        response = self.client.get("/api/v1/space/?complete=1&published=0")
        self.assertEqual(self._has_space_in_response(response), True)

        response = self.client.get("/api/v1/space/?complete=1")
        self.assertEqual(self._has_space_in_response(response), True)

        # With the bug, the second put to remove data does the right thing...
        response = self.client.put(self.url, '{"location.latitude":"","location.longitude":"","extended_info.campus":"seattle"}', content_type="application/json")
        response = self.client.put(self.url, '{"location.latitude":"","location.longitude":"","extended_info.campus":"seattle"}', content_type="application/json")

        response = self.client.get("/api/v1/space/?complete=0&published=0")
        self.assertEqual(self._has_space_in_response(response), True)

        response = self.client.get("/api/v1/space/?complete=1&published=0")
        self.assertEqual(self._has_space_in_response(response), False)

        response = self.client.get("/api/v1/space/?complete=1")
        self.assertEqual(self._has_space_in_response(response), False)

        # Reset and break...
        response = self.client.put(self.url, '{"location.latitude":"47.651952","location.longitude":"-122.303141","extended_info.campus":"seattle"}', content_type="application/json")
        response = self.client.put(self.url, '{"location.latitude":"","location.longitude":"","extended_info.campus":"seattle"}', content_type="application/json")

        response = self.client.get("/api/v1/space/?complete=0&published=0")
        self.assertEqual(self._has_space_in_response(response), True)

        response = self.client.get("/api/v1/space/?complete=1&published=0")
        self.assertEqual(self._has_space_in_response(response), False)

        response = self.client.get("/api/v1/space/?complete=1")
        self.assertEqual(self._has_space_in_response(response), False)


    def _has_space_in_response(self, response):
        data = json.loads(response.content)
        for el in data:
            if ("%s" % el["id"]) == ("%s" % self.space_id):
                return True
        return False

