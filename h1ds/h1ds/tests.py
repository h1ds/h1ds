import os
import tempfile
import uuid

import tables
from django.test import TestCase

from h1ds.models import Device, Shot, Tree

def generate_temp_filename():
    return os.path.join(tempfile.gettempdir(), 'h1ds_'+str(uuid.uuid4().get_hex()[0:12]))

class WritableDeviceTestCase(TestCase):
    def setUp(self):
        self.temp_files = []
        self.device_names = {'read_only':'readonly_hdf5_device',
                             'read_write':'readwrite_hdf5_device'}
        self.readonly_device = Device.objects.create(name=self.device_names['read_only'],
                                description='Test HDF5 Device (read only)',
                                data_backend='hdf5',
                                read_only=True)
        self.readonly_device.full_clean()
        
        self.readwrite_device = Device.objects.create(name=self.device_names['read_write'],
                                description='Test HDF5 Device (read/write)',
                                data_backend='hdf5',
                                read_only=False)
        self.readwrite_device.full_clean()


    def tearDown(self):
        for f in self.temp_files:
            if os.path.exists(f):
                os.remove(f)

class DeviceBackendTestCase(TestCase):

    def test_mds_backend(self):
        device = Device.objects.create(name='test_mds_device',
                                description='Test MDS Device',
                                data_backend='mds')
        device.full_clean()
        

    def test_h1_backend(self):
        device = Device.objects.create(name='test_h1_device',
                                description='Test H1 Device',
                                data_backend='h1')
        device.full_clean()
        
    
    def test_hdf5_backend(self):
        device = Device.objects.create(name='test_hdf5_device',
                                description='Test HDF5 Device',
                                data_backend='hdf5')
        device.full_clean()

class WebAPIPutShotTest(WritableDeviceTestCase):

    def test_read_write_device(self):
        shot_number = 1
        response = self.client.put('/data/{}/{}/'.format(self.device_names['read_write'], shot_number))
        self.assertEqual(response.status_code, 200)
        
        new_shot = Shot.objects.get(device=self.readwrite_device, number=shot_number)

    def test_read_only_device(self):
        shot_number = 1
        response = self.client.put('/data/{}/{}/'.format(self.device_names['read_only'], shot_number))
        self.assertEqual(response.status_code, 405)
        
        #shot should not appear
        with self.assertRaises(Shot.DoesNotExist):
            Shot.objects.get(device=self.readonly_device, number=shot_number)
        


class WebApiPutTreeTest(WritableDeviceTestCase):

    def test_read_write_device(self):
        shot_number = 1
        tree_name = 'test_tree_1'
        response = self.client.put('/data/{}/{}/{}/'.format(self.device_names['read_write'], shot_number, tree_name))
        self.assertEqual(response.status_code, 200)
        
        new_shot = Shot.objects.get(device=self.readwrite_device, number=shot_number)

        new_tree = Tree.objects.get(device=self.readwrite_device, name=tree_name)

    def test_read_only_device(self):
        shot_number = 1
        tree_name = 'test_tree_1'
        response = self.client.put('/data/{}/{}/{}/'.format(self.device_names['read_only'], shot_number, tree_name))
        self.assertEqual(response.status_code, 405)
        
        #shot should not appear
        with self.assertRaises(Shot.DoesNotExist):
            Shot.objects.get(device=self.readonly_device, number=shot_number)

        with self.assertRaises(Tree.DoesNotExist):
            Tree.objects.get(device=self.readonly_device, name=tree_name)

class TestHdf5Tree(WritableDeviceTestCase):

    def test_create_hdf5_tree(self):
        hdf5_filename = generate_temp_filename()
        tree = Tree.objects.create(device=self.readwrite_device, name='test_tree', configuration=hdf5_filename, data_backend='hdf5')

        ### tree shouldn't exist if tree created, only touch file when creating data. for tree, the model instance is enough
        with self.assertRaises(IOError):
            h5file = tables.open_file(hdf5_filename, mode = "r", title = "test file")

