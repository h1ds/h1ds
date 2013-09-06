from distutils.core import setup

execfile('h1ds_configdb/version.py')

setup(name='h1ds_configdb',
      version=__version__,
      packages=['h1ds_configdb'],
      )
