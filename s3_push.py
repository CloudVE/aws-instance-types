from os import listdir
from os.path import isfile, join

from cloudbridge.factory import CloudProviderFactory
from cloudbridge.factory import ProviderList

vmtypes_dirpath = 'vmtypes/'

aws = CloudProviderFactory().create_provider(ProviderList.AWS, {})

bucket = aws.storage.buckets.get('aws-vm-types')

for zone_file in listdir(vmtypes_dirpath):
    path = join(vmtypes_dirpath, zone_file)
    if isfile(path):
        o = bucket.objects.create(zone_file)
        o.upload_from_file(path)
        o._obj.put(ACL='public-read')
