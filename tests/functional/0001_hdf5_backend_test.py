"""

Backends:
 - MDSPlus
 - HDF5

"""

import os
import json
#from selenium import webdriver
from django.test import TestCase
from django.utils import unittest
from h1ds.models import Device, Shot
import tempfile
import uuid
import tables

CT_JSON ='application/json'

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
        response = self.client.put('/data/test_hdf5_device/1/', content_type=CT_JSON)
        self.assertEqual(response.status_code, 200)

        new_shot = Shot.objects.get(device=self.device, number=1)

        # use http post/put to create branches, data etc

        # make sure the new data appears in html

    def test_generate_tree(self):
        test_file = generate_temp_filename()
        self.temp_files.append(test_file)
        json_data = json.dumps({'configuration':test_file})
        response = self.client.put('/data/test_hdf5_device/1/diagnostics/', data=json_data, content_type=CT_JSON)
        self.assertEqual(response.status_code, 200)

        # the file should now exist
        h5file = tables.open_file(test_file, mode = "r", title = "test file")
        h5file.close()
        # And should have a single empty group for shot 1

        # Now add a group (url path component)
        response = self.client.put('/data/test_hdf5_device/1/diagnostics/density/', content_type=CT_JSON)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/data/test_hdf5_device/1/diagnostics/density/')

        # now let's put some data in.

        data = {}
        data['name'] = 'Test_density_data'
        data['value'] = [range(100), range(100)]
        data['dimension'] = [range(100)]
        data['metadata'] = {'tag_a': True, 'tag_b': 'a_string', 'tag_c':42}
        data['value_labels'] = ['Channel A', 'Channel B']
        data['dimension_labels'] = ['Time']
        data['value_units'] = ['Volts', 'Volts']
        data['dimension_units'] = ['Seconds']
        url_path = '/data/test_hdf5_device/1/diagnostics/density/test_signal/'
        json_data = json.dumps({'data':data})
        response = self.client.put(url_path, data=json_data, content_type=CT_JSON)

        response = self.client.get(url_path+'?format=json')
        response_data = json.loads(response.content)['data']

        self.assertEqual(data['name'], response_data['name'])
        self.assertEqual(data['value'], response_data['value'])
        self.assertEqual(data['dimension'], response_data['dimension'])
        self.assertEqual(data['metadata'], response_data['metadata'])
        self.assertEqual(data['value_labels'], response_data['value_labels'])
        self.assertEqual(data['dimension_labels'], response_data['dimension_labels'])
        self.assertEqual(data['value_units'], response_data['value_units'])
        self.assertEqual(data['dimension_units'], response_data['dimension_units'])
        
        
    def test_read_only_tree(self):
        # create a writeable device
        # create a read only tree
        # make sure that we can't PUT to the tree.
        pass
        
if __name__ == '__main__':
    unittest.main()
