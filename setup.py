from setuptools import setup, find_packages

execfile('h1ds/version.py')

setup(name='h1ds',
      version=__version__,
      description="A data access system for nuclear fusion experiments",
      author = "David Pretty",
      author_email="david.pretty@gmail.com",
      packages=find_packages(),
	include_package_data = True,
      )
