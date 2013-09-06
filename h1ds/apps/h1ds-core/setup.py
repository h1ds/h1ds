from distutils.core import setup

execfile('h1ds_core/version.py')

setup(name='h1ds_core',
      version=__version__,
      packages=['h1ds_core'],
      package_data={'h1ds_core':['app_media/h1ds_core/css/*.css', 'templates/*/*.html']}
      )
