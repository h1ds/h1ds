"""
Scan files for metadata.

The  settings.H1DS_CONFIGDB_METADATA_FUNCTION function  is to  extract
metadata. Directories scanned are those provided by ConfigDBLoadingDir
instances.
"""
import os
import shutil
import random

from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File

from h1ds_configdb.models import ConfigDBLoadingDir
from h1ds_configdb import CONFIGDB_SUBFOLDER
from h1ds_configdb.utils import scan_configdb_dir

CONFIGDB_PATH = os.path.join(settings.MEDIA_ROOT, CONFIGDB_SUBFOLDER)
metadata_scanner = settings.H1DS_CONFIGDB_METADATA_FUNCTION

class Command(BaseCommand):
    args = ''
    help = 'Scan configdb directory for metadata'

    def handle(self, *args, **options):
        #if not os.path.exists(CONFIGDB_PATH):
        #    os.mkdir(CONFIGDB_PATH)

        for d in ConfigDBLoadingDir.objects.all():
            self.stdout.write("Scanning directory: %s" %d.folder)
            scan_configdb_dir(d.folder, d.force_overwrite)
