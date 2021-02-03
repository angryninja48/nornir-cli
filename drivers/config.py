from drivers.base import BaseHandler

from typing import Optional
from nornir.core.task import Task, Result
from nornir_jinja2.plugins.tasks import template_file
from nornir_napalm.plugins.tasks import napalm_configure
from nornir_netmiko.tasks.netmiko_send_command import netmiko_send_command

import logging
import os

logger = logging.getLogger(__name__)

class NapalmConfigure(BaseHandler):
    """
    Napalm based tasks for Nornir
    """
    @staticmethod
    def napalm_config_run(
        task: Task, configuration: str, dry_run: Optional[bool] = True, replace: Optional[bool] = False
        ) -> Result:

        result = task.run(
            task=napalm_configure,
            dry_run=dry_run,
            replace=replace,
            configuration=configuration
        )
        # TODO: Fix up output
        return Result(host=task.host, result=result.result, failed=False, changed=False)

    @staticmethod
    def render_template(
        task: Task, template_name: str, template_path: Optional[str] = None
        ) -> Result:
        
        from jinja2 import Environment, FileSystemLoader, StrictUndefined
        logger.info(f"{task.host}: Rendering Config")

        if not template_path:
            template_path = os.path.join(os.getcwd(), f'templates/{task.host.platform}')

        env = Environment(
                    loader=FileSystemLoader(template_path), undefined=StrictUndefined, trim_blocks=False,
        )

        result = task.run(
                task=template_file,
                name='Render Device Configuration',
                template=f'{template_name}.j2',
                jinja_env=env,
                path=template_path,
                **task.host
        )
        return Result(host=task.host, result=result.result, failed=False, changed=False)

    @staticmethod
    def render_template_apply(
        task: Task, template_name: str, template_path: Optional[str] = None
        ) -> Result:
        
        from jinja2 import Environment, FileSystemLoader, StrictUndefined
        logger.info(f"{task.host}: Rendering Config")

        if not template_path:
            template_path = os.path.join(os.getcwd(), f'templates/{task.host.platform}')

        env = Environment(
                    loader=FileSystemLoader(template_path), undefined=StrictUndefined, trim_blocks=False,
        )

        config = task.run(
                task=template_file,
                name='Render Device Configuration',
                template=f'{template_name}.j2',
                jinja_env=env,
                path=template_path,
                **task.host
        )

        result = task.run(
            task=napalm_configure,
            dry_run=False,
            replace=False,
            configuration=config.result
        )

        return Result(host=task.host, result=result.result, failed=False, changed=False)

    def apply_merge_template(
        self, template_name: str, dry_run: Optional[bool] = True
        ):
        """
        Merge configuration based off a template
        """

        config = self.nornir.run(
            task=self.render_template_apply, 
            template_name=template_name
        )

        return config

    def apply_merge_config(
        self, config: str, dry_run: Optional[bool] = True
        ):
        """
        Merge configuration based off a string input
        """
        result = self.nornir.run(
            task=self.napalm_config_run,
            name='Merge config to device',
            dry_run=dry_run,
            replace=False,
            configuration=config
        )

        # Fix up return Currently == None
        return result

class NetmikoConfigure(BaseHandler):
    """
    Netmiko based tasks for Nornir
    """
    @staticmethod
    def netmiko_command_run(
        task: Task, command: str
        ) -> Result:

        try:
            result = task.run(
                task=netmiko_send_command,
                command_string=command
            )

        except NornirSubTaskError:
            pass
            # logger.debug(f"{task.host}: An error occured while running the command: {command}")

        # TODO: Fix up output

        return Result(host=task.host, result=result.result, failed=False, changed=False)

    def send_command(
        self, command: str
        ):
        result = self.nornir.run(
            task=self.netmiko_command_run, 
            command=command
        )
        return result