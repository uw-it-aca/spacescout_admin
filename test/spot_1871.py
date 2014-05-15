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
class Spot1871(TestCase):
    def test_post(self):
        admins, created = Group.objects.get_or_create(name="spacescout_admins")
        user = User.objects.create_user("test_user", "test@example.com", "ok")

        admins.user_set.add(user)

        self.client = Client()
        self.client.login(username="test_user", password="ok")

        response = self.client.post("/api/v1/space/", '{ "name": "test_space_1871", "manager": "javerage" }', content_type="application/json")

        data = json.loads(response.content)

        self.assertEqual(type(data), type({}))
