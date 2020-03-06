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
    print("Getting all VM Types")
    r = requests.get(info_json_url)
    print("Successfully reached: " + info_json_url)
    data = r.json()
    # keeping entire dict to not invalidate "extra_data" property in
    # CloudBridge
    vm_types = {}
    for entry in data:
        vm_types[entry['instance_type']] = entry
    return vm_types


def get_info_for_vm_type(vm_type_id):
    all_info = get_all_info_from_json_file()
    vmtype_info = all_info.get(vm_type_id, None)
    if vmtype_info and vmtype_info.get("pricing", None):
    	# Removing pricing information to make files smaller
    	vmtype_info.pop('pricing')
    return vmtype_info

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
    print("Calling 'aws.ec2_conn.meta.client.describe_reserved_instances_offerings'")
    result = (aws.ec2_conn.meta.client
                 .describe_reserved_instances_offerings(
                     AvailabilityZone=zone_name))
    ids = list(set(offering.get('InstanceType') for offering
                   in result.get('ReservedInstancesOfferings')))
    print("Gathered {} vmtypes from the first page".format(len(ids)))
    # Stop if 10 pages in a row did not add any VM
    num = len(ids)
    count = 0
    while result.get('NextToken') and count < 50:
        print("Gathering next page")
        result = (aws.ec2_conn.meta.client
                     .describe_reserved_instances_offerings(
                         AvailabilityZone=zone_name,
                         NextToken=result.get('NextToken')))
        for offering in result.get('ReservedInstancesOfferings'):
            vm_type_id = offering.get('InstanceType')
            if vm_type_id not in ids:
                ids.append(vm_type_id)
        if len(ids) == num:
            count += 1
        else:
            count = 0
            num = len(ids)
    # Removing instances that we don't have information about from the
    # json file. eg: r5.metal, m5d.metal, z1d.metal
    print("Total {} vmtypes after gathering all pages".format(len(ids)))
    vm_types = []
    for type_id in ids:
        type_dict = get_info_for_vm_type(type_id)
        if type_dict:
            vm_types.append(type_dict)
    return vm_types


def update_files_for_first_third():
    regions = get_all_region_names()
    regions = regions[:int(len(regions)/3)]
    print("Regions for which zones will be updated:")
    print(regions)
    for region in regions:
        zones = get_all_zones_in_region(region)
        for zone in zones:
            print("Zone currently being updated:")
            print(zone)
            with open(vmtypes_dirpath + zone + '.json', 'w') as file:
                file.write(json.dumps((list_vm_types_in_zone(zone))))


def update_files_for_second_third():
    regions = get_all_region_names()
    regions = regions[int(len(regions)/3):2*int(len(regions)/3)]
    print("Regions for which zones will be updated:")
    print(regions)
    for region in regions:
        zones = get_all_zones_in_region(region)
        for zone in zones:
            print("Zone currently being updated:")
            print(zone)
            with open(vmtypes_dirpath + zone + '.json', 'w') as file:
                file.write(json.dumps((list_vm_types_in_zone(zone))))


def update_files_for_last_third():
    regions = get_all_region_names()
    regions = regions[2*int(len(regions)/3):]
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
    part = sys.argv[1]
    if part == 'test':
        update_files_test()
    elif part == 'first':
        update_files_for_first_third()
    elif part == 'second':
        update_files_for_second_third()
    elif part == 'third':
        update_files_for_last_third()
    else:
        msg = 'The script takes a string argument.\n' \
              'Accepted values are: [first, second, third, test]\n' \
              'Example: python3 update_files.py first\n'
        print(msg)


if __name__ == '__main__':
    main()
    print("Done :)")
