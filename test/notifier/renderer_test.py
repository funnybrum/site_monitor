from os.path import join
from datetime import datetime

from unittest import TestCase

from test import TEST_TEMPLATES_FOLDER

from monitor.models.config import Config
from monitor.models.item import Item, Event
from monitor.notifier.renderer import HTMLGenerator


class RendererTest(TestCase):
    def test_renderer_base_v4(self):

        config = Config({
            'template': join(TEST_TEMPLATES_FOLDER, 'base_v4.html'),
            'template_config': {},
            'send_new': True,
            'send_updates': True,
            'send_deletes': True
        })

        generator = HTMLGenerator(config)

        item1 = Item({
            'key': 'item1_key',
            'link': 'http://some/test',
            'attributes': {
                'image': 'http://some/image.gif',
                'price': '100.5 BGN',
                'description': 'This is a test item',
                'area': '@somewhere'
            },
            'events': [
                self._create_event(1, 'event 1'),
                self._create_event(2, 'event 2')
            ]
        })

        item1.is_new = True
        item1.is_updated = False
        item1.is_deleted = False

        messages = [
            'message 1',
            'message 2',
            'message 3'
        ]

        rendered_html = generator.generate([item1], messages)
        print rendered_html

    @staticmethod
    def _create_event(day, text):
        return Event({
            'datetime': datetime(2017, 10, day, 0, 0, 0),
            'text': text
        }).to_primitive()