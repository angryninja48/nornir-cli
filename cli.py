from main import InitNr
from moovr.iosgetters import NapalmIOSGetter

a = InitNr()
nr = a.nornir

getters = NapalmIOSGetter()
method = getattr(getters, 'get_facts')
result = nr.run(task=method)
print(result['csr01'][0])
