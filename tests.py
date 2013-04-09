"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from spacescout_admin.utils import *
from django.core.files import File
from django.core.files.uploadedfile import UploadedFile


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
