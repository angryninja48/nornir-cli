import csv
import json
from ttp import ttp

from main import InitNr
from tasks.iosgetters import NapalmIOSGetter

from netaddr import IPNetwork, IPAddress

OUTPUT_DIR='./outputs'

ttp_template = """
<group name="interfaces.{{ interface }}">
interface {{ interface }}
 description {{ description }}
 ip address {{ ipv4_address }} {{ subnet }}
 ip helper-address {{ helper_address | _line_ | joinmatches | to_list }}
</group>
"""

def interface_parser(config):
    parser = ttp(data=config, template=ttp_template)
    parser.parse()
    interfaces = parser.result()[0][0]
    return interfaces

def get_network(ipv4, mask):
    try:
        network = IPNetwork(f'{ipv4}/{mask}').cidr
    except:
        return None
    return network

# def get_ips():
#     a = InitNr()
#     nr = a.nornir
#     getters = NapalmIOSGetter()
#     # Grab the Interface IP's
#     method = getattr(getters, 'get_interfaces_ip')
#     result = nr.run(task=method)
#     # Build a dict with the results
#     d = {}
#     for hostname, values in result.items():
#         d[hostname] = values.result
#     return d

# def ip_facts():
#     d = get_ips()
    
#     # Loop through each host
#     results = []
#     for host, interfaces in d.items():

#         # Loop through each interface
#         for interface, addr in interfaces.items():
#             ipv4_dict = addr.get('ipv4')
#             if ipv4_dict:
#                 for address, prefix in ipv4_dict.items():
#                     prefix_length = prefix.get('prefix_length')
#                     cidr = f"{address}/{prefix_length}"
#                     network = get_network(cidr)
#                     results.append(
#                         {
#                             "hostname": host,
#                             "interface": interface,
#                             "address": address,
#                             "prefix_length": prefix_length,
#                             "cidr": cidr,
#                             "network": str(network),
#                         }
#                     )
#     return results


def get_l3_facts():
    a = InitNr()
    nr = a.nornir
    getters = NapalmIOSGetter()
    # Grab the Config
    method = getattr(getters, 'get_config')
    configs = nr.run(task=method)
    # Parse out interface config and build a dictionary with network key
    results = {}
    for host, config in configs.items():
        # Handle Failed hosts
        if not config.failed:
            interfaces = interface_parser(config.result)['interfaces']
            for k,v in interfaces.items():
                try:
                    interfaces[k]['network'] = str(get_network(ipv4=v['ipv4_address'], mask=v['subnet']))
                except:
                    pass
            results[host] = interfaces

        else:
            results[host] = {}

    return results
                    
def main():

    # Get configs and dump interfaces to file
    # facts = get_l3_facts()
    facts={'csr01': {'Loopback0': {'ipv4_address': '10.244.194.1', 'subnet': '255.255.255.240', 'network': '10.244.194.0/28'}, 'GigabitEthernet1': {'description': 'vagrant-management','network': '10.20.0.0/24', 'helper_address': ['1.1.1.1', '2.2.2.2']}, 'GigabitEthernet2': {'ipv4_address': '10.20.0.100', 'subnet': '255.255.255.0', 'network': '10.20.0.0/24'}}, 'csr02': {}}
    # print(facts)

    # # Dump facts to file
    # with open(f'{OUTPUT_DIR}/facts.json', 'w') as outfile:
    #     json.dump(facts, outfile)

    # # Read in csv
    inputfile = 'networks.csv'
    with open(inputfile, "r", newline="") as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames
        list_of_nets = [row['Network'] for row in reader]

    # Match up networks and build a list
    results = []
    for host, interfaces in facts.items():
        if interfaces:
            for network in list_of_nets:
                for k,i in interfaces.items():
                    if (
                        ('network' in i) and
                        (network in i['network'])
                    ):
                        device = facts[host][k]
                        device['hostname'] = host
                        device['interface'] = k
                        results.append(device)

    # print(results)

    #     if host
    #     import ipdb; ipdb.set_trace()
    #     for i in interfaces.values():
    #         print(i)
    #     # if 'ipv4_address' in interfaces:
    #     #     print(True)
    # # Loop through both lists and return only the matching networks
    # results = []
    # for i in ipfacts:
    #     for network in list_of_nets:
    #         if network in i['network']:
    #             results.append(
    #                     {
    #                         "hostname": i['hostname'],
    #                         "interface": i['interface'],
    #                         "address": i['address'],
    #                         "prefix_length": i['prefix_length'],
    #                         "cidr": i['cidr'],
    #                         "network": i['network'],
    #                     }
    #                 )
    # # Output to new csv
    outputfile = f'{OUTPUT_DIR}/network_facts.csv'
    # fieldnames = list(results[0].keys())
    fieldnames =[
        'hostname',
        'interface',
        'description',
        'ipv4_address',
        'subnet',
        'network',
        'helper_address',
    ]
    with open(outputfile, "w", newline="") as f:
        writer = csv.DictWriter(f,fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == '__main__':
    main()
