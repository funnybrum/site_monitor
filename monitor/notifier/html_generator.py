from jinja2 import (
    Environment,
    PackageLoader
)
import datetime


class HTMLGenerator(object):
    def __init__(self, config):
        self.template = config.template
        self.template_config = config.template_config
        self.send_new = config.send_new
        self.send_updates = config.send_updates
        self.send_deletes = config.send_deletes

    def generate(self, new, removed, updated):
        """
        Format the given new/deleted and old items into proper HTML message body.

        :param new:
        :param updated:
        :param removed:
        :return:
        """
        env = Environment(loader=PackageLoader('prop_monitor', 'templates'))
        template = env.get_template(self.template)
        return template.render(
            {
                'config': self.template_config,
                'data': {
                    'new': new if self.send_new else {},
                    'updated': updated if self.send_updates else {},
                    'removed': removed if self.send_deletes else {},
                },
                'as_of': datetime.datetime.now()
            }
        )
