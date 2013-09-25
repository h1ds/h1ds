import hashlib

import os
from django.conf import settings
from django.core.files import File
from h1ds_configdb.models import ConfigDBFile, ConfigDBFileType
from h1ds_configdb.models import ConfigDBPropertyType, ConfigDBProperty
from h1ds_configdb.models import value_type_mapping


def dummy_metadata_scanner(full_filename):
    raise NotImplementedError


metadata_scanner = getattr(settings,
                           "H1DS_CONFIGDB_METADATA_FUNCTION",
                           dummy_metadata_scanner)


def md5_for_filename(fn, block_size=2 ** 20):
    with open(fn, 'rb') as f:
        md5 = hashlib.md5()
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


def scan_configdb_dir(configdb_dir, force_overwrite):
    for root, dirs, files in os.walk(configdb_dir):
        for fn in files:
            full_filename = os.path.join(root, fn)

            # Check whether md5 hash for file is in the database.
            file_md5 = md5_for_filename(full_filename)
            md5_in_db = ConfigDBFile.objects.filter(md5sum=file_md5).count() > 0

            if md5_in_db and not force_overwrite:
                continue

            try:
                filetype, mimetype, metadata = metadata_scanner(full_filename)
            except NotImplementedError:
                continue


            # If there is no filetype  model instance for this filetype, create
            # one.
            ft_inst, ft_created = ConfigDBFileType.objects.get_or_create(
                name=filetype,
                defaults={'mimetype': mimetype}
            )

            # Make  sure the  mimetype  here  is the  same  as  that stored  in
            # database.
            if ft_inst.mimetype != mimetype:
                raise ValueError('wrong mimetype')

            dbfile_inst, dbfile_created = ConfigDBFile.objects.get_or_create(
                dbfile=File(open(full_filename)),
                md5sum=file_md5,
                defaults={'filetype': ft_inst}
            )

            for (k, v) in metadata.items():
                value_type = value_type_mapping.get(type(v))
                if (value_type != None) and (k not in ['filename', 'filetype']):
                    pt_inst, pt_c = ConfigDBPropertyType.objects.get_or_create(
                        name=k,
                        value_type=value_type,
                        defaults={'description': 'No description'}
                    )

                    new_property = ConfigDBProperty(
                        configdb_file=dbfile_inst,
                        configdb_propertytype=pt_inst,
                    )
                    new_property.__setattr__('value_' + value_type.lower(), v)
                    new_property.save()
