HDF5 Backend
============

A basic `PyTables <http://pytables.org>`_ based HDF5 backend is provided.

Following the H1DS ``/device/shot/tree/nodepath`` URL scheme, a HDF5 datafile corresponds to a ``h1ds.models.Tree`` instance.

The hdf5 data filename is specified in Tree.configuration.


Using HTTP PUT to ``/device/shot`` will add to the shot index (entry into relational database) but will not create a HDF5 file as no tree is specified (and the tree contains the hdf5 config info).

A HDF5 file is only created (if it doesn't exist) when HTTP PUT specifies a tree.

The relationship between tree and shot within a HDF5 file is the reverse of that in the URL API, that is, while the tree corresponds to the hdf5 file itself, shots exist as groups at the root level in the file.


