from drivers.config import NapalmConfigure, NetmikoConfigure

# Instantiate
napc = NapalmConfigure()
netc = NetmikoConfigure()

# Set inventory

netc.inventory(host_file='inventory/site2/hosts.yml', group_file='inventory/site2/groups.yml', defaults_file='inventory/defaults.yml')
napc.inventory(host_file='inventory/site2/hosts.yml', group_file='inventory/site2/groups.yml', defaults_file='inventory/defaults.yml')

config = 'interface GigabitEthernet2\n description jb-test'

a = napc.apply_merge_config(config=config, dry_run=False)

print(a['csr01'].result)

# sh_ver = netc.send_command(command='show version')
# sh_int = netc.send_command(command='show version')


# # import ipdb;ipdb.set_trace()
# print(sh_ver['csr01'].result)
# print(sh_int['csr02'].result)

