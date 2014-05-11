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
        pass

    def tearDown(self):
        #self.browser.quit()
        pass

    def test_generate_hdf5_test_shot_via_api(self):
        shot_numbers = xrange(1,10)
        device = Device.objects.create(name='test_hdf5_device',
                                description='Test HDF5 Device',
                                data_backend='hdf5')
        
        generate_test_data(device, shot_numbers)

        for shot_number in shot_numbers:
            shot = Shot.objects.get(device=device, number=shot_number)
        
        # check URLs to make sure we can see the data
        #response = self.client.get('/data/test_hdf5_device/1/')
        #assert 'operations' in response
        #assert 'diagnostics' in response
        


        

if __name__ == '__main__':
    unittest.main()
