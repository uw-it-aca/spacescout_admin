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
from spacescout_admin.models import Space, SpaceEditor
import json

@override_settings(SS_ADMIN_FIELDS_MODULE='spacescout_admin.field_definitions.default')
@override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
class Spot1303(TestCase):
    def test_change_ownership(self):
        creators, created = Group.objects.get_or_create(name="spacescout_creators")
        admins, created = Group.objects.get_or_create(name="spacescout_admins")

        admin_user = User.objects.create_user("admin_user", "test@example.com", "ok")
        admins.user_set.add(admin_user)

        creator_user1 = User.objects.create_user("creator_user1", "test1@example.com", "ok")
        creators.user_set.add(creator_user1)
        creator_user2 = User.objects.create_user("creator_user2", "test2@example.com", "ok")
        creators.user_set.add(creator_user2)


        # Create the space as a creator user
        self.client = Client()
        self.client.login(username="creator_user1", password="ok")
        response = self.client.post("/api/v1/space/", '{ "name": "test_space", "manager": "creator_user1" }', content_type="application/json")
        data = json.loads(response.content)

        url = "/api/v1/space/%s/" % data["id"]
        pk = int(data["id"])
        space = Space.objects.get(pk = pk)
        self.assertEqual(space.manager, "creator_user1")

        # As an admin, change the manager

        self.client.logout()
        self.client.login(username="admin_user", password="ok")
        response = self.client.put(url, '{ "manager": "creator_user2" }', content_type="application/json")

        space = Space.objects.get(pk = pk)

        self.assertEqual(space.manager, "creator_user2")
