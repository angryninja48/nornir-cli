import csv
import json
from ttp import ttp

from main import InitNr
from tasks.iosgetters import NapalmIOSGetter

from netaddr import IPNetwork

OUTPUT_DIR='./outputs'

ttp_template = """
<group name="interfaces.{{ interface }}">
interface {{ interface }}
<group>
 ip helper-address {{ helper_address }}
</group>
</group>
"""

def interface_parser(config):
    parser = ttp(data=config, template=ttp_template)
    parser.parse()
    interfaces = parser.result()[0][0]
    return interfaces

def get_interface_dhcp():
    a = InitNr()
    nr = a.nornir
    getters = NapalmIOSGetter()
    # Grab the Interface IP's
    method = getattr(getters, 'get_config')
    result = nr.run(task=method)

def get_network(ipv4=None):
    try:
        network = IPNetwork(ipv4).cidr
    except:
        return None
    return network

def get_ips():
    a = InitNr()
    nr = a.nornir
    getters = NapalmIOSGetter()
    # Grab the Interface IP's
    method = getattr(getters, 'get_interfaces_ip')
    result = nr.run(task=method)
    # Build a dict with the results
    d = {}
    for hostname, values in result.items():
        d[hostname] = values.result
    return d

def ip_facts():
    d = get_ips()
    
    # Loop through each host
    results = []
    for host, interfaces in d.items():

        # Loop through each interface
        for interface, addr in interfaces.items():
            ipv4_dict = addr.get('ipv4')
            if ipv4_dict:
                for address, prefix in ipv4_dict.items():
                    prefix_length = prefix.get('prefix_length')
                    cidr = f"{address}/{prefix_length}"
                    network = get_network(cidr)
                    results.append(
                        {
                            "hostname": host,
                            "interface": interface,
                            "address": address,
                            "prefix_length": prefix_length,
                            "cidr": cidr,
                            "network": str(network),
                        }
                    )
    return results


def interface_helpers():
    a = InitNr()
    nr = a.nornir
    getters = NapalmIOSGetter()
    # Grab the Config
    method = getattr(getters, 'get_config')
    configs = nr.run(task=method)
    # Parse out interface config
    results = []
    for host, config in configs.items():
        interfaces = interface_parser(config.result)['interfaces']
        for interface, address in interfaces.items():
            if address:
                results.append(
                        {
                            "hostname": host,
                            "interface": interface,
                            "helpers": address,
                        }
                    )
    return results

def main():

    # Get configs and dump interfaces to file
    interfaces = interface_helpers()

    with open(f'{OUTPUT_DIR}/interface_helpers.json', 'w') as outfile:
        json.dump(interfaces, outfile)

    # Gather facts from the devices using nornir
    ipfacts = ip_facts()

    # Read in csv
    inputfile = 'networks.csv'
    with open(inputfile, "r", newline="") as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames
        list_of_nets = [row['Network'] for row in reader]

    # Loop through both lists and return only the matching networks
    results = []
    for i in ipfacts:
        for network in list_of_nets:
            if network in i['network']:
                results.append(
                        {
                            "hostname": i['hostname'],
                            "interface": i['interface'],
                            "address": i['address'],
                            "prefix_length": i['prefix_length'],
                            "cidr": i['cidr'],
                            "network": i['network'],
                        }
                    )
    # Output to new csv
    outputfile = f'{OUTPUT_DIR}/network_facts.csv'
    fieldnames = list(results[0].keys())
    with open(outputfile, "w", newline="") as f:
        writer = csv.DictWriter(f,fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == '__main__':
    main()
