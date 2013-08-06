"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test.client import Client
from django.test import TestCase
from django.core.files import File
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth.models import User, Group, Permission
from spacescout_admin.models import QueuedSpace
from spacescout_admin.views import edit_space
from spacescout_admin.forms import QueueForm
from spacescout_admin.utils import *
import json


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_download_excel(self):
        datastr = '[{"extended_info": {"location_description": "Kitchen in Test building in test ocean","has_trashcans": "\u201ctrue\u201d","campus": "not"}, "manager": "King Piccolo", "last_modified": "2013-03-19T23:09:35.375447+00:00","display_access_restrictions": "","id": "9001","capacity": "12","name": "American Test Kitchen","uri": "/api/v1/spot/9001","available_hours": {"monday": [["07:30", "17:30"]], "tuesday": [["07:30", "17:30"]], "friday": [["07:30", "17:30"]], "wednesday": [["07:30", "17:30"]], "thursday": [["07:30", "17:30"]], "sunday": [["10:00", "17:00"]], "saturday": [["09:00", "15:00"]]},"location": {"floor": "2nd floor","height_from_sea_level": "-10","room_number": "meeeeep","longitude": "-122.316432","latitude": "-47.652953","building_name": "Test Building"}, "organization": "beepbeep","type": ["lounge"]}]'
        data = json.loads(datastr)
        excel = write_xls(data)
        data = data[0]
        excelfile = open('spacescout_admin/test_xls1.xls', 'w')
        excelfile.write(excel.content)
        excelfile.close()
        data1 = file_to_json(UploadedFile(open('spacescout_admin/test_xls1.xls', 'r'), content_type='application/vnd.ms-excel'))
        data1 = json.loads(data1['data'][0]['data'])
        unused_keys = set([u'id', u'uri', u'display_access_restrictions', u'last_modified'])  # id and uri are pulled out (to put to that uri, which contains the id), display_access_restrictions is empty, and last_modified is generated dynamically
        self.assertEqual((set(data) - set(data1)), unused_keys)
        for key in unused_keys:
            del data[key]

        self.assertEqual(data, data1)

    def test_download_csv(self):
        datastr = '[{"extended_info": {"location_description": "Kitchen in Test building in test ocean","has_trashcans": "\u201ctrue\u201d","campus": "not"}, "manager": "King Piccolo", "last_modified": "2013-03-19T23:09:35.375447+00:00","display_access_restrictions": "","id": "9001","capacity": "12","name": "American Test Kitchen","uri": "/api/v1/spot/9001","available_hours": {"monday": [["07:30", "17:30"]], "tuesday": [["07:30", "17:30"]], "friday": [["07:30", "17:30"]], "wednesday": [["07:30", "17:30"]], "thursday": [["07:30", "17:30"]], "sunday": [["10:00", "17:00"]], "saturday": [["09:00", "15:00"]]},"location": {"floor": "2nd floor","height_from_sea_level": "-10","room_number": "meeeeep","longitude": "-122.316432","latitude": "-47.652953","building_name": "Test Building"}, "organization": "beepbeep","type": ["lounge"]}]'
        data = json.loads(datastr)
        csv = write_csv(data)
        data = data[0]
        csvfile = open('spacescout_admin/test_csv1.csv', 'w')
        csvfile.write(csv.content)
        csvfile.close()
        data1 = file_to_json(UploadedFile(open('spacescout_admin/test_csv1.csv', 'r'), content_type='text/csv'))
        data1 = json.loads(data1['data'][0]['data'])
        unused_keys = set([u'id', u'uri', u'display_access_restrictions', u'last_modified'])  # id and uri are pulled out (to put to that uri, which contains the id), display_access_restrictions is empty, and last_modified is generated dynamically
        self.assertEqual((set(data) - set(data1)), unused_keys)
        for key in unused_keys:
            del data[key]

        self.assertEqual(data, data1)

    def test_unauthorized_spot_editing(self):
        c = Client()

        # Create a user
        self.nonmanager = User.objects.create_user(username='nonmanager', password='pass', email='nonmanager@uw.edu')

        # Give user permissions required to edit a spot, generally, but not a manager of any spot
        can_update = Permission.objects.get(codename='can_update')
        self.nonmanager.user_permissions.add(can_update)

        # Create a group that has permission to edit the space
        test_group = Group.objects.create(name="test")

        # Initialize a spot that has different manager than user
        before_json = '{"manager": ["test"], "capacity": 12, "location": {"floor": "2nd floor", "latitude": 47.652956, "room_number": 207, "longitude": -122.316343, "building_name": "Fishery Sciences (FSH)"}}'
        before_queued_space = {
            "id": 1,
            "json": before_json,
            "errors": "{}",
            "space_etag": "x34C%6v9b&n9x234c48V 5rb-n-[a",
            "q_etag": None,
            "status": "updated",
            "approved_by": None,
        }
        before_form = QueueForm(before_queued_space)
        self.assertEqual(before_form.is_valid(), True, "Makes sure the form is valid")
        before_space = before_form.save(commit=False)
        before_space.space_last_modified = "2013-05-08T20:25:09.490751+00:00"
        before_space.modified_by = self.nonmanager
        before_space.space_id = 1
        before_space.save()
        q_etag = before_space.q_etag

        # Comment out below to not add the user to the group
        # self.nonmanager.groups.add(test_group)

        # Login the user that doesn't have the correct permissions
        c.login(username='nonmanager', password='pass')

        # As that user, edit some data for that spot
        # In the POST request, none of the data gets nested like how the server expects. the data POSTed is flat
        after_json = {"manager": ["test"], "capacity": 200, "floor": "roof", "q_id": 1, "q_etag": q_etag, "latitude": 47.652956, "room_number": 1, "longitude": -3, "building_name": "Different"}
        after_queued_space = before_queued_space
        del after_queued_space["json"]
        for item in after_json:
            after_queued_space.update({item: after_json[item]})
        after_queued_space.update({"space_last_modified": before_space.space_last_modified, "modified_by": before_space.modified_by})

        # Pass different json as a request.POST
        response = c.post('/space/1', after_queued_space)

        # Log the user out
        c.logout()

        # Get the spot data
        space = QueuedSpace.objects.get(space_id=1)

        # Check that the json matches the original and not the modified
        self.assertEqual(json.loads(space.json), json.loads(before_json), "Make sure the spot data matches the original json and not the data modified by the non-manager.")
