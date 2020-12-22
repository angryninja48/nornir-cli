
from nornir.core.task import Task, Result
from nornir_napalm.plugins.tasks import napalm_get

import logging

logger = logging.getLogger(__name__)

class NapalmIOSGetter:
    """
    Napalm based tasks for Nornir
    """
    @staticmethod
    def get_facts(task: Task):
        logger.info(f"{task.host}: Getting Facts")
        
        result = task.run(
           task=napalm_get,
           name="Get Facts from device",
           getters=['facts']
        ) 

        if not result:
            logger.info(f"{task.host}: Failed to get facts")
            return Result(host=task.host, failed=True, changed=False)

        facts = result.result['facts']
        logger.info(f"{task.host}: Facts Retrieved")

        return Result(host=task.host, result=facts, failed=False, changed=False)
    
    @staticmethod
    def get_config(task: Task):
        logger.info(f"{task.host}: Getting Running Config")
        
        # try:
        result = task.run(
            task=napalm_get,
            name="Get Running configs from device",
            getters=['config']
        )
        # except NornirSubTaskError as e:
        #     logger.info(f"{task.host}: Failed to get running config")
        #     task.results.pop()

        if not result:
            logger.info(f"{task.host}: Failed to get running config")
            return Result(host=task.host, failed=True, changed=False)

        config = result.result['config']['running']

        logger.info(f"{task.host}: Config Retrieved")
    
        return Result(host=task.host, result=config, failed=False, changed=False)

    @staticmethod
    def get_interfaces_ip(task: Task):
        logger.info(f"{task.host}: Getting Interface IP Addresses")

        result = task.run(
            task=napalm_get,
            name="Get IP addresses from device",
            getters=['interfaces_ip']
        )
        if not result:
            logger.info(f"{task.host}: Failed to get interfaces")
            return Result(host=task.host, failed=True, changed=False)

        ints = result.result['interfaces_ip']

        logger.info(f"{task.host}: Interfaces Retrieved")
    
        return Result(host=task.host, result=ints, failed=False, changed=False)


class NetmikoIOSGetter:
    """
    Netmiko based tasks for Nornir
    """