from django.test import TestCase
from h1ds.models import Device, generate_test_data

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


class GenerateTestDataTestCase(TestCase):

    def test_generated_data(self):
        shot_numbers = xrange(1,5)
        device = Device.objects.create(name='test_hdf5_device',
                                description='Test HDF5 Device',
                                data_backend='hdf5')
        generate_test_data(device, shot_numbers)

class ReadWriteDeviceTest(TestCase):

    def test_read_write_device(self):
        device = Device.objects.create(name='test_hdf5_device',
                                description='Test HDF5 Device',
                                data_backend='hdf5',
                                read_only=False)
        device.full_clean()
        
