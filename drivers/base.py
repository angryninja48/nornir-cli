

import os

from getpass import getpass

from nornir import InitNornir
from nornir.core.filter import F

class BaseHandler:
    """
    Wrapper for Nornir
    """
    def __init__(self, nornir=None):
        self.nornir = nornir

        if not self.nornir:
            self.inventory(host_file='inventory/site1/hosts.yml', group_file='inventory/site1/groups.yml', defaults_file='inventory/defaults.yml')

    # Init Nornir, filter inventory and set crednetials
    def inventory(self, host_file, group_file, defaults_file, num_workers=1, device_filter=None, 
                group_filter=None, vault_file=None, vault_pass=None, output_directory='./outputs'):

        self.num_workers = num_workers
        self.host_file = host_file
        self.group_file = group_file
        self.defaults_file = defaults_file
        self.device_filter = device_filter
        self.group_filter = group_filter
        self.output_directory = output_directory
        self.vault_file = vault_file
        self.vault_pass = vault_pass

        self.nornir = InitNornir(
            runner={
                'plugin': 'threaded',
                'options':{
                    'num_workers': self.num_workers
                }
            },
            inventory={
                "options": {
                    "host_file": self.host_file,
                    "group_file": self.group_file,
                    "defaults_file": self.defaults_file
                }
            }
        )

        if self.device_filter is not None:
            self.nornir.filter(F(name__contains=self.device_filter))
        
        if self.group_filter is not None:
            self.nornir.filter(F(name__contains=self.group_filter))

        if self.vault_file is not None:
            print(f'Please enter vault credentials')
            if self.vault_pass is None:
                self.vault_pass = getpass()
            self.nornir.inventory.defaults.data['secrets'] = decrypt_file(self.vault_file, self.vault_pass)

        return self.nornir


