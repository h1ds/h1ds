H1DS data types (under development).
====================================

This docuement specifies the data types currently used by H1DS. 

This specification is expected to be revised prior to version 1.0.

The SubTree model has the following properties related to data (the metadata which is indexed).

has_data = models.BooleanField(default=True)
n_dimensions = models.PositiveSmallIntegerField(blank=True, null=True)
dtype = models.CharField(max_length=16, blank=True)
n_channels = models.PositiveSmallIntegerField(blank=True, null=True)


As such, a node can currently have just one dtype associated with it.

SubTree.get_data() returns an instance of h1ds.base.Data

name: string
value: [dim1, dim2,...]  dim_n are themselves lists
dimension = [dim1, dim2, ...]
value_units = str
dimension_units = str
value_dtype = str
dimension_dtype = str
value_labels = [dim1_str, dim2_str,...]
dimension_labels = [dim1_str, dim2_str, ...]
metadata = dict



for scalar (10)
value = [10]
dimension= []

for multichannel (same dimension) 1d signal, e.g.3 channels with same timebase

value = [[[1,2,3,4], [1,2,3,4], [1,2,3,4]]]
dimension = [[1,2,3,4]]

