import json
import requests
import sys

import cachetools

from cloudbridge.factory import CloudProviderFactory
from cloudbridge.factory import ProviderList

aws = CloudProviderFactory().create_provider(ProviderList.AWS, {})

info_json_url = 'https://cdn.rawgit.com/powdahound/ec2instances' \
                '.info/master/www/instances.json'

vmtypes_dirpath = 'vmtypes/'


@cachetools.cached(cachetools.TTLCache(maxsize=1, ttl=24*3600))
def get_all_info_from_json_file():
    r = requests.get(info_json_url)
    data = r.json()
    # keeping entire dict to not invalidate "extra_data" property in
    # CloudBridge
    vm_types = {}
    for entry in data:
        vm_types[entry['instance_type']] = entry
    return vm_types


def get_info_for_vm_type(vm_type_id):
    all_info = get_all_info_from_json_file()
    return all_info.get(vm_type_id, None)


def get_all_region_names():
    return [region['RegionName'] for region in
            aws.ec2_conn.meta.client.describe_regions().get('Regions')]


def get_all_zones_in_region(region_name):
    aws._ec2_conn = aws._connect_ec2_region(region_name)
    allz = (aws.ec2_conn.meta.client
               .describe_availability_zones(Filters=[{'Name': 'region-name',
                                                      'Values':[region_name]}])
               .get('AvailabilityZones'))
    return [zone.get('ZoneName') for zone in allz]


def list_vm_types_in_zone(zone_name):
    result = (aws.ec2_conn.meta.client
                 .describe_reserved_instances_offerings(
                     AvailabilityZone=zone_name))
    ids = list(set(offering.get('InstanceType') for offering
                   in result.get('ReservedInstancesOfferings')))
    while result.get('NextToken'):
        result = (aws.ec2_conn.meta.client
                     .describe_reserved_instances_offerings(
                         AvailabilityZone=zone_name,
                         NextToken=result.get('NextToken')))
        for offering in result.get('ReservedInstancesOfferings'):
            vm_type_id = offering.get('InstanceType')
            if vm_type_id not in ids:
                ids.append(vm_type_id)
    # Removing instances that we don't have information about from the
    # json file. eg: r5.metal, m5d.metal, z1d.metal
    vm_types = []
    for type_id in ids:
        type_dict = get_info_for_vm_type(type_id)
        if type_dict:
            vm_types.append(type_dict)
    return vm_types


def update_files_for_first_half():
    regions = get_all_region_names()
    regions = regions[:int(len(regions)/2)]
    print("Regions for which zones will be updated:")
    print(regions)
    for region in regions:
        zones = get_all_zones_in_region(region)
        for zone in zones:
            print("Zone currently being updated:")
            print(zone)
            with open(vmtypes_dirpath + zone + '.json', 'w') as file:
                file.write(json.dumps((list_vm_types_in_zone(zone))))


def update_files_for_second_half():
    regions = get_all_region_names()
    regions = regions[int(len(regions)/2):]
    print("Regions for which zones will be updated:")
    print(regions)
    for region in regions:
        zones = get_all_zones_in_region(region)
        for zone in zones:
            print("Zone currently being updated:")
            print(zone)
            with open(vmtypes_dirpath + zone + '.json', 'w') as file:
                file.write(json.dumps((list_vm_types_in_zone(zone))))


def update_files_test():
    regions = get_all_region_names()
    regions = regions[0:1]
    print("Regions for which zones will be updated:")
    print(regions)
    for region in regions:
        zones = get_all_zones_in_region(region)
        for zone in zones[0:1]:
            print("Zone currently being updated:")
            print(zone)
            with open(vmtypes_dirpath + zone + '.json', 'w') as file:
                file.write(json.dumps((list_vm_types_in_zone(zone))))


def main():
    half = sys.argv[1]
    if half == 'test':
        update_files_test()
    elif half == 'first':
        update_files_for_first_half()
    elif half == 'second':
        update_files_for_second_half()
    else:
        msg = 'The script takes a string argument.\n' \
              'Accepted values are: [first, second]\n' \
              'Example: python3 update_files.py first\n'
        print(msg)


if __name__ == '__main__':
    main()
    print("Done :)")
