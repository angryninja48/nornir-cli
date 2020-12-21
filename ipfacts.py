from main import InitNr
from tasks.iosgetters import NapalmIOSGetter

from netaddr import IPNetwork

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

def main():
    ipfacts = ip_facts()

    list_of_nets = [
        '10.0.0.0/27',
        '10.244.194.0/28',
        '10.0.2.0/24'
    ]

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
    print(results)

if __name__ == '__main__':
    main()
