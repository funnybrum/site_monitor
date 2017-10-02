from unittest import TestCase

from test import TEST_CONFIG_FOLDER

from monitor.models.item import Item
from monitor.monitor import Monitor
from monitor.config.loader import ConfigLoader


class MonitorTest(TestCase):
    def test_update_prcess_new_item(self):
        monitor = self._create_monitor()
        item = Item({
            'key': '1',
            'link': 'http://fake.url',
            'attributes': {},
            'events': []
        })

        monitor.update(
            {
                '1': item
            },
            {})

        self.assertEqual(1, len(item.events))
        self.assertEqual('created', item.events[0].text)

    def test_update_prcess_deleted_item(self):
        monitor = self._create_monitor()
        item = Item({
            'key': '1',
            'link': 'http://fake.url',
            'attributes': {},
            'events': [monitor._create_event('created')]
        })

        items = {}
        monitor.update(
            items,
            {
                '1': item
            })

        self.assertEqual(1, len(items))
        self.assertTrue('1' in items)
        item = items['1']
        self.assertEqual(2, len(item.events))
        self.assertEqual('created', item.events[0].text)
        self.assertEqual('deleted', item.events[1].text)

    def test_update_prcess_updated_item(self):
        monitor = self._create_monitor()
        old_item = Item({
            'key': '1',
            'link': 'http://fake.url',
            'attributes': {
                'at1': 'val1',
                'at2': 'val2',
                'at3': 'val3'
            },
            'events': [monitor._create_event('created')]
        })

        new_item = Item({
            'key': '1',
            'link': 'http://fake.url',
            'attributes': {
                'at1': 'val1',
                'at2': 'val2_v2',
                'at3': 'val3_v2'
            },
            'events': [monitor._create_event('created')]
        })

        new_items = {'1': new_item}
        old_items = {'1': old_item}

        monitor.update(new_items, old_items)

        self.assertEqual(1, len(new_items))
        self.assertTrue('1' in new_items)
        item = new_items['1']
        self.assertEqual(3, len(item.events))
        self.assertEqual('created', item.events[0].text)
        self.assertTrue(item.events[1].text.endswith('v2'))
        self.assertTrue(item.events[2].text.endswith('v2'))

    def test_update_prcess_updated_deleted_item(self):
        monitor = self._create_monitor()
        old_item = Item({
            'key': '1',
            'link': 'http://fake.url',
            'attributes': {
                'at1': 'val1',
                'at2': 'val2',
                'at3': 'val3'
            },
            'events': [monitor._create_event('created'), monitor._create_event('deleted')]
        })

        new_item = Item({
            'key': '1',
            'link': 'http://fake.url',
            'attributes': {
                'at1': 'val1',
                'at2': 'val2_v2',
                'at3': 'val3_v2'
            },
            'events': [monitor._create_event('created')]
        })

        new_items = {'1': new_item}
        old_items = {'1': old_item}

        monitor.update(new_items, old_items)

        self.assertEqual(1, len(new_items))
        self.assertTrue('1' in new_items)
        item = new_items['1']
        self.assertEqual(5, len(item.events))
        self.assertEqual('re-created', item.events[2].text)

    def _create_monitor(self):
        config = ConfigLoader.load_all_configs(TEST_CONFIG_FOLDER)[0]
        return Monitor(config)
