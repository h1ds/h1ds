"""Test that a user can create a device via the admin interface for each backend.

Backends:
 - MDSPlus
 - HDF5

"""

import os
#from selenium import webdriver
from django.test import TestCase
from django.utils import unittest
from h1ds.models import Device, Shot
import tempfile
import uuid
import tables

def generate_temp_filename():
    return os.path.join(tempfile.gettempdir(), 'h1ds_'+str(uuid.uuid4().get_hex()[0:12]))

class Hdf5BackendTest(TestCase):

    def setUp(self):
        #self.browser = webdriver.Firefox()
        self.temp_files = []
        self.device = Device.objects.create(name='test_hdf5_device',
                                    description='Test HDF5 Device',
                                    data_backend='hdf5',
                                    read_only=False)

    def tearDown(self):
        #self.browser.quit()
        for f in self.temp_files:
            if os.path.exists(f):
                os.remove(f)
    
    def test_generate_hdf5_test_shot_via_api(self):

        # use http post/put to create a new shot
        response = self.client.put('/data/test_hdf5_device/1/')
        self.assertEqual(response.status_code, 200)

        new_shot = Shot.objects.get(device=self.device, number=1)

        # use http post/put to create branches, data etc

        # make sure the new data appears in html

    def test_generate_tree(self):
        test_file = generate_temp_filename()
        self.temp_files.append(test_file)
        response = self.client.put('/data/test_hdf5_device/1/diagnostics/', data={'description', test_file})
        self.assertEqual(response.status_code, 200)

        # the file should not exist yet - it should only be created when nodepath is included (see docs/backends/hdf5.rst)
        with self.assertRaises(IOError):
            h5file = tables.open_file(test_file, mode = "r", title = "test file")
        

    def test_generate_pathnode(self):
        pass

        

if __name__ == '__main__':
    unittest.main()
