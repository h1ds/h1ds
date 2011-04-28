from distutils.core import setup

execfile('h1ds_summary/version.py')

setup(name='h1ds_summary',
      version=__version__,
      packages=['h1ds_summary','h1ds_summary.migrations'],
      )
