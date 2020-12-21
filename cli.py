from main import InitNr
from tasks.iosgetters import NapalmIOSGetter

a = InitNr()
nr = a.nornir

getters = NapalmIOSGetter()
# method = getattr(getters, 'get_facts')
# method = getattr(getters, 'get_config')
method = getattr(getters, 'get_interfaces_ip')


result = nr.run(task=method)
print(result)
