Components of H1DS
==================

Major components
----------------

Device: represents an experimental setup, e.g. plasma confinement device

Shot: a single operational run of the device, an experiment.

Tree: root of a hierachical dataset for a device. In general the same tree struture is present for multiple shots

ShotRange: A continuous range of shots -- simply a (min, max) pair. A tree can have mulitple shot ranges.

NodePath: a node identifier use to relate a node between different shots.

SubTree: A node of the data tree which knows about metadata (dtype, n_dim, n_channels, children (other sub trees)). The subtree doesn't know about node path, shot, or the actual data, so an instance can be used in several places in a data tree, and across shots. 

Node: A mapping of a subtree to nodepath for a given shot.

