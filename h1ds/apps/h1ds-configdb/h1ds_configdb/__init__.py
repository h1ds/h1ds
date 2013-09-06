"""Configurations database for H1NF."""

from django.conf import settings

if hasattr(settings, "H1DS_CONFIGDB_ROOT_URL"):
    MODULE_ROOT_URL = settings.H1DS_CONFIGDB_ROOT_URL
else:
    MODULE_ROOT_URL = "configurations" 

# Name to be used for this module in H1DS header, footer links, etc.
MODULE_DOC_NAME = "Configurations"

# subfolder under MEDIA_ROOT to put configdb files
CONFIGDB_SUBFOLDER = "configdb"
