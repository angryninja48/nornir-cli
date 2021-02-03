from drivers.base import BaseHandler

from nornir.core.task import Result
from nornir_jinja2.plugins.tasks import template_file

import logging
import os

logger = logging.getLogger(__name__)

class Templates(BaseHandler):
    """
    Render Jinja2 templates using Nornir
    """
    # def __init__(self, template=None):
    #     self.template = template

    @staticmethod
    def _render_config(task, template_name, template_path=None):
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

        if not result:
            logger.info(f"{task.host}: Failed to render configg")
            return Result(host=task.host, failed=True, changed=False)

        config = result.result
        logger.info(f"{task.host}: Config Rendered")

        return Result(host=task.host, result=config, failed=False, changed=False)

    def render_config(self, template_name, save=False):
        result = self.nornir.run(
                task=self._render_config,
                name='Render Device Configuration',
                template_name=template_name,
        )
        if save:
            for k,v in result.items():
              self.save_to_file(file_name=k,config=v.result)

        return result

    def save_to_file(self, file_name, config):
        try:
            with open(f'output/{file_name}.conf', "a") as file:
                file.write(config)
                file.close()
                logger.info(f"{file_name}: Successfully saved config")

        except Exception as e:
            logger.info(f"{file_name}: Failed to save config")
