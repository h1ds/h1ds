from django.test import TestCase
from h1ds.models import Device, Shot

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




class ReadWriteDeviceTest(TestCase):

    def test_read_write_device(self):
        device = Device.objects.create(name='test_hdf5_device',
                                description='Test HDF5 Device',
                                data_backend='hdf5',
                                read_only=False)
        device.full_clean()

        response = self.client.put('/data/test_hdf5_device/1/')
        self.assertEqual(response.status_code, 200)
        
        new_shot = Shot.objects.get(device=device, number=1)
        
        
        
class ReadOnlyDeviceTest(TestCase):
    
    def test_read_write_device(self):
        # default should be read only
        device = Device.objects.create(name='test_hdf5_device',
                                description='Test HDF5 Device',
                                data_backend='hdf5')
        device.full_clean()

        response = self.client.put('/data/test_hdf5_device/1/')
        self.assertEqual(response.status_code, 405)

        #shot should not appear
        with self.assertRaises(Shot.DoesNotExist):
            Shot.objects.get(device=device, number=1)
