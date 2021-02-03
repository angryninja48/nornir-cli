from drivers.getters import NapalmGetter

y = NapalmGetter()
a = y.get_facts()
b = y.get_config()
c = y.get_interfaces_ip()

print(a['csr01'].result)
print(b['csr01'].result)
print(c['csr01'].result)