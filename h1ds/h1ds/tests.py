"""
Currently only HTTP PUT and GET are tested.
"""
import json
import os
import tempfile
import uuid

import numpy as np

import tables
from django.test import TestCase

from h1ds.models import Device, Shot, Tree, Node, ShotRange, NodePath

CT_JSON ='application/json'


def generate_temp_filename():
    return os.path.join(tempfile.gettempdir(), 'h1ds_'+str(uuid.uuid4().get_hex()[0:12]))

class WritableHDF5DeviceTestCase(TestCase):
    """Simple base class which adds devices and clears temp files."""

    
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
    """Make sure we can create a device for each backend."""

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

############################################################
## HDF5 tests
############################################################
        
class WebAPIPutShotTest(WritableHDF5DeviceTestCase):
    """Test we can add a shot to a writable device but not a read-only one."""
    
    def test_read_write_device(self):
        shot_number = 1
        url_path = '/data/{}/{}/'.format(self.device_names['read_write'], shot_number)
        response = self.client.put(url_path, content_type=CT_JSON)
        self.assertEqual(response.status_code, 200)
        
        shot_a = Shot.objects.get(device=self.readwrite_device, number=shot_number)

        response = self.client.get(url_path)
        self.assertEqual(response.status_code, 200)

        # HTTP PUT is idempotent, so we should get HTTP 200 again if we try to put the shot again.
        response = self.client.put(url_path, content_type=CT_JSON)
        self.assertEqual(response.status_code, 200)

        # check if shot object is the same
        shot_b = Shot.objects.get(device=self.readwrite_device, number=shot_number)
        self.assertEqual(shot_a, shot_b)
        

    def test_read_only_device(self):
        shot_number = 1
        response = self.client.put('/data/{}/{}/'.format(self.device_names['read_only'], shot_number), content_type=CT_JSON)
        self.assertEqual(response.status_code, 405)
        
        #shot should not appear
        with self.assertRaises(Shot.DoesNotExist):
            Shot.objects.get(device=self.readonly_device, number=shot_number)
        


class WebApiPutHDF5TreeTest(WritableHDF5DeviceTestCase):

    def test_read_write_device(self):
        shot_number = 1
        tree_name = 'test_tree_1'
        url_path = '/data/{}/{}/{}/'.format(self.device_names['read_write'], shot_number, tree_name)
        hdf5_filename = generate_temp_filename()
        self.temp_files.append(hdf5_filename)
        json_data = json.dumps({'configuration': hdf5_filename, 'data_backend':'hdf5'})
        response = self.client.put(url_path, data=json_data, content_type=CT_JSON)
        self.assertEqual(response.status_code, 200)
        
        new_shot = Shot.objects.get(device=self.readwrite_device, number=shot_number)

        tree_a = Tree.objects.get(device=self.readwrite_device, name=tree_name)

        # check that ShotRange is created.
        self.assertEqual(tree_a.shot_ranges.count(), 1)
        
        # check that we can get the tree
        response = self.client.get('/data/{}/{}/{}/'.format(self.device_names['read_write'], shot_number, tree_name))
        self.assertEqual(response.status_code, 200)

        # check that HTTP PUT is idempotent
        response = self.client.put(url_path, data=json_data, content_type=CT_JSON)
        self.assertEqual(response.status_code, 200)
        tree_b = Tree.objects.get(device=self.readwrite_device, name=tree_name)
        self.assertEqual(tree_a, tree_b)

    def test_read_only_device(self):
        shot_number = 1
        tree_name = 'test_tree_1'
        response = self.client.put('/data/{}/{}/{}/'.format(self.device_names['read_only'], shot_number, tree_name),content_type=CT_JSON)
        self.assertEqual(response.status_code, 405)
        
        #shot should not appear
        with self.assertRaises(Shot.DoesNotExist):
            Shot.objects.get(device=self.readonly_device, number=shot_number)

        with self.assertRaises(Tree.DoesNotExist):
            Tree.objects.get(device=self.readonly_device, name=tree_name)

class WebApiPutHDF5NodeTest(WritableHDF5DeviceTestCase):

    def test_node_without_data(self):
        shot_number = 1
        tree_name = 'test_tree_1'
        tree_url_path = '/data/{}/{}/{}/'.format(self.device_names['read_write'], shot_number, tree_name)
        hdf5_filename = generate_temp_filename()
        self.temp_files.append(hdf5_filename)
        json_data = json.dumps({'configuration': hdf5_filename, 'data_backend':'hdf5'})
        response = self.client.put(tree_url_path, data=json_data, content_type=CT_JSON)
        self.assertEqual(response.status_code, 200)

        # create a group node (url path component without data)
        node_name = 'test_group_node_1'
        url_path = '/data/{}/{}/{}/{}/'.format(self.device_names['read_write'], shot_number, tree_name, node_name)
        response = self.client.put(url_path, content_type=CT_JSON)
        self.assertEqual(response.status_code, 200)

        # check that corresponding node is created
        nodepath = NodePath.objects.get(path=node_name)
        node = Node.objects.get(node_path=nodepath, shot__number=shot_number)
        self.assertFalse(node.subtree.has_data)

        response = self.client.get(url_path)
        self.assertEqual(response.status_code, 200)

        # make sure HTTP PUT is idempotent
        response = self.client.put(url_path, content_type=CT_JSON)
        self.assertEqual(response.status_code, 200)

    def test_node_with_data(self):
        # our test data
        data = {}
        data['name'] = 'test_1d_data'
        data['value'] = [range(100)]
        data['dimension'] = [range(100)]
        data['value_units'] = 'volts'
        data['dimension_units'] = 'seconds'
        data['value_dtype'] = 'int'
        data['dimension_dtype'] = 'int'
        json_node_data = json.dumps({'data':data})
        
        shot_number = 1
        tree_name = 'test_tree_2'
        tree_url_path = '/data/{}/{}/{}/'.format(self.device_names['read_write'], shot_number, tree_name)
        hdf5_filename = generate_temp_filename()
        self.temp_files.append(hdf5_filename)
        json_data = json.dumps({'configuration': hdf5_filename, 'data_backend':'hdf5'})
        response = self.client.put(tree_url_path, data=json_data, content_type=CT_JSON)
        self.assertEqual(response.status_code, 200)

        # create a group node (url path component without data)
        node_name = 'test_group_node_1'
        url_path = '/data/{}/{}/{}/{}/'.format(self.device_names['read_write'], shot_number, tree_name, node_name)
        response = self.client.put(url_path, data=json_node_data, content_type=CT_JSON)
        self.assertEqual(response.status_code, 200)

        # check that corresponding node is created
        nodepath = NodePath.objects.get(path=node_name)
        node = Node.objects.get(node_path=nodepath, shot__number=shot_number)
        self.assertTrue(node.subtree.has_data)

        response = self.client.get(url_path)
        self.assertEqual(response.status_code, 200)

        # make sure HTTP PUT is idempotent
        response = self.client.put(url_path, content_type=CT_JSON)
        self.assertEqual(response.status_code, 200)

                
class HDF5DataTest(WritableHDF5DeviceTestCase):
    """Test consistency between data uploaded via API and the HDF5 backend.

    This checks each datatype as scalar, 1d and multichannel.

    For more on H1DS data types, see docs/reference/datatypes.rst
        
    """
    def test_scalar(self):
        pass

    
    
    def test_1d_signal(self):
        # our test data
        data = {}
        data['name'] = 'test_1d_data'
        data['value'] = [range(100)]
        data['dimension'] = [range(100)]
        data['value_units'] = 'volts'
        data['dimension_units'] = 'seconds'
        data['value_dtype'] = 'int'
        data['dimension_dtype'] = 'int'
        json_data = json.dumps({'data':data})
        
        tree_url_path = '/'.join(['', 'data', self.device_names['read_write'], '1', 'diagnostics'])
        node_url_path = '/'.join([tree_url_path, 'diag1', data['name'], ''])

        hdf5_filename = generate_temp_filename()
        self.temp_files.append(hdf5_filename)
        
        # create tree first
        response = self.client.put(tree_url_path+'/', data=json.dumps({'configuration': hdf5_filename}), content_type=CT_JSON)
        # put the node 
        response = self.client.put(node_url_path, data=json_data, content_type=CT_JSON)

        # NEXT open file and check data is there...
        f = tables.open_file(hdf5_filename, mode='r',title='test file')
        self.assertTrue('shot_1' in f.root)
        self.assertTrue('diag1' in f.root.shot_1)
        hdf5_node = f.get_node("/shot_1/diag1", data['name'])
        #self.assertEqual(hdf5_node.name, data['name'])
        self.assertTrue(np.array_equal(hdf5_node.value.read(), data['value']))
        self.assertTrue(np.array_equal(hdf5_node.dimension.read(), data['dimension']))
        
        f.close()
        
class Hdf5GetTest(WritableHDF5DeviceTestCase):
    """Make sure we can read data from HDF5 tree via HTTP GET."""

    def test_1d_signal(self):
        """
        TODO: refactor: lots of duplicated between here and Hdf5DataTest.
        """
        data = {}
        data['name'] = 'test_1d_data'
        data['value'] = [range(100)]
        data['dimension'] = [range(100)]
        data['value_units'] = 'volts'
        data['dimension_units'] = 'seconds'
        data['value_dtype'] = 'int'
        data['dimension_dtype'] = 'int'
        data['value_labels'] = ['Channel A']
        data['dimension_labels'] = ['Channel A']
        data['metadata'] = {'tag_a': True, 'tag_b': 'some_string', 'tag_c': 42}
        json_data = json.dumps({'data':data})
        
        tree_url_path = '/'.join(['', 'data', self.device_names['read_write'], '1', 'diagnostics'])
        node_url_path = '/'.join([tree_url_path, 'diag1', 'test_data_node', ''])

        hdf5_filename = generate_temp_filename()
        self.temp_files.append(hdf5_filename)
        
        # create tree first
        response = self.client.put(tree_url_path+'/', data=json.dumps({'configuration': hdf5_filename}), content_type=CT_JSON)
        # put the node 
        response = self.client.put(node_url_path, data=json_data, content_type=CT_JSON)

        response = self.client.get(node_url_path+'?format=json')
        returned_data = json.loads(response.content)['data']
        
        # we should get the same data that we put in.
        self.assertEqual(returned_data['name'], data['name'])
        self.assertEqual(returned_data['value'], data['value'])
        self.assertEqual(returned_data['dimension'], data['dimension'])
        self.assertEqual(returned_data['value_units'], data['value_units'])
        self.assertEqual(returned_data['dimension_units'], data['dimension_units'])
        self.assertEqual(returned_data['value_dtype'], data['value_dtype'])
        self.assertEqual(returned_data['dimension_dtype'], data['dimension_dtype'])
        self.assertEqual(returned_data['value_labels'], data['value_labels'])
        self.assertEqual(returned_data['dimension_labels'], data['dimension_labels'])
        self.assertEqual(returned_data['metadata'], data['metadata'])
        
                            
class Hdf5TreeTest(WritableHDF5DeviceTestCase):

    def test_create_empty_hdf5_tree(self):
        hdf5_filename = generate_temp_filename()
        self.temp_files.append(hdf5_filename)
        tree = Tree.objects.create(device=self.readwrite_device, name='test_tree', configuration=hdf5_filename, data_backend='hdf5')

        # file should now exist
        hdf5_file = tables.open_file(hdf5_filename, mode = "r", title = "test file")
        # without any nodes
        self.assertEqual(len(hdf5_file.list_nodes("/")), 0)
        hdf5_file.close()

    def test_create_hdf5_tree(self):
        hdf5_filename = generate_temp_filename()
        self.temp_files.append(hdf5_filename)
        shot_range = ShotRange(min_shot=1, max_shot=1)
        shot_range.save()
        tree, created = Tree.objects.get_or_create(device=self.readwrite_device, name='test_tree', configuration=hdf5_filename, data_backend='hdf5')
        tree.shot_ranges.add(shot_range)
        tree.save()
        
        # file should now exist
        hdf5_file = tables.open_file(hdf5_filename, mode = "r", title = "test file")
        # without any nodes
        self.assertEqual(len(hdf5_file.list_nodes("/")), 1)
        hdf5_file.close()

class SubTreeTest(WritableHDF5DeviceTestCase):
    """make sure subtree integrity is maintained if we put data within an existing subtree."""
    pass
    

