"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_download_excel(self):
        f1 = UploadedFile(open('/home/qnnwp/spotseeker-admin/spotseeker_admin/test_xls.xls', 'r'), content_type='application/vnd.ms-excel')
        data = file_to_json(f1)
        spots = [json.loads(data['data'][0]['data'][0:-1] + ', "id": ' + data['data'][0]['id'] + "}")]
        excel = write_xls(spots)
        f2 = open('test_xls1.xls', 'w')
        f2.write(excel.content)
        f2.close()
        f2 = UploadedFile(open('test_xls1.xls', 'r'), content_type='application/vnd.ms-excel')
        data1 = file_to_json(f2)
        self.assertEquals(json.loads(data['data'][0]['data']), json.loads(data1['data'][0]['data']))

    def test_download_csv(self):
        f1 = UploadedFile(open('/home/qnnwp/spotseeker-admin/spotseeker_admin/test_csv.csv', 'r'), content_type='text/csv')
        data = file_to_json(f1)
        spots = [json.loads(data['data'][0]['data'][0:-1] + ', "id": ' + data['data'][0]['id'] + "}")]
        csv = write_csv(spots)
        f2 = open('test_csv1.csv', 'w')
        f2.write(csv.content)
        f2.close()
        f2 = UploadedFile(open('test_csv1.csv', 'r'), content_type='text/csv')
        data1 = file_to_json(f2)
        self.assertEquals(json.loads(data['data'][0]['data']), json.loads(data1['data'][0]['data']))
