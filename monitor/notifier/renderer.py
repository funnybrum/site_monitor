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

    def generate(self, items, messages):
        """
        Render the given items and messages into proper HTML message body.
        :return:
        """
        env = Environment(loader=PackageLoader('prop_monitor', 'templates'))
        template = env.get_template(self.template)
        return template.render(
            {
                'config': self.template_config,
                'data': {
                    'new': [item for item in items if item.is_new and self.send_new],
                    'updated': [item for item in items if item.is_updated and self.send_updates],
                    'removed': [item for item in items if item.is_deleted and self.send_deletes],
                },
                'messages': messages,
                'as_of': datetime.datetime.now()
            }
        )
