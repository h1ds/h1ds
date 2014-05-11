"""Test that a user can create a device via the admin interface for each backend.

Backends:
 - MDSPlus
 - HDF5

"""

#from selenium import webdriver
from django.test import TestCase
from django.utils import unittest
from h1ds.models import Device, Shot, generate_test_data


class GenerateHdf5TestShotTest(TestCase):

    def setUp(self):
        #self.browser = webdriver.Firefox()
        self.device = Device.objects.create(name='test_hdf5_device',
                                    description='Test HDF5 Device',
                                    data_backend='hdf5',
                                    read_only=False)

    def tearDown(self):
        #self.browser.quit()
        pass

    def test_generate_hdf5_test_shot_via_api(self):

        # use http post/put to create a new shot
        response = self.client.put('/data/test_hdf5_device/1/')
        self.assertEqual(response.status_code, 200)

        new_shot = Shot.objects.get(device=self.device, number=1)

        # use http post/put to create branches, data etc

        # make sure the new data appears in html

    def test_generate_tree(self):
        pass

    def test_generate_pathnode(self):
        pass

        

if __name__ == '__main__':
    unittest.main()
