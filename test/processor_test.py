from unittest import TestCase

from test import TEST_CONFIG_FOLDER

from monitor.models.item import Item
from monitor.processors.history_creator import HistoryCreator
from monitor.config.loader import ConfigLoader


class ProcessorTest(TestCase):
    def setUp(self):
        config = ConfigLoader.load_all_configs(TEST_CONFIG_FOLDER)[0]
        self.history_creator = HistoryCreator(config)

    def test_update_prcess_new_item(self):
        item = Item({
            'key': '1',
            'link': 'http://fake.url',
            'attributes': {},
            'events': []
        })

        item = self.history_creator.process(
            {
                '1': item
            },
            {}).values()[0]

        self.assertEqual(1, len(item.events))
        self.assertEqual('created', item.events[0].text)
        self.assertTrue(item.is_new)
        self.assertFalse(item.is_deleted)
        self.assertFalse(item.is_updated)

    def test_update_prcess_deleted_item(self):
        item = Item({
            'key': '1',
            'link': 'http://fake.url',
            'attributes': {},
            'events': [self.history_creator._create_event('created')]
        })

        items = {}
        items = self.history_creator.process(
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
        self.assertTrue(item.is_deleted)
        self.assertFalse(item.is_new)
        self.assertFalse(item.is_updated)

    def test_update_prcess_updated_item(self):
        old_item = Item({
            'key': '1',
            'link': 'http://fake.url',
            'attributes': {
                'at1': 'val1',
                'at2': 'val2',
                'at3': 'val3'
            },
            'events': [self.history_creator._create_event('created')]
        })

        new_item = Item({
            'key': '1',
            'link': 'http://fake.url',
            'attributes': {
                'at1': 'val1',
                'at2': 'val2_v2',
                'at3': 'val3_v2'
            },
            'events': [self.history_creator._create_event('created')]
        })

        new_items = {'1': new_item}
        old_items = {'1': old_item}

        new_items = self.history_creator.process(new_items, old_items)

        self.assertEqual(1, len(new_items))
        self.assertTrue('1' in new_items)
        item = new_items['1']
        self.assertEqual(3, len(item.events))
        self.assertEqual('created', item.events[0].text)
        self.assertTrue(item.events[1].text.endswith('v2'))
        self.assertTrue(item.events[2].text.endswith('v2'))
        self.assertTrue(item.is_updated)
        self.assertFalse(item.is_new)
        self.assertFalse(item.is_deleted)

    def test_update_prcess_updated_deleted_item(self):
        old_item = Item({
            'key': '1',
            'link': 'http://fake.url',
            'attributes': {
                'at1': 'val1',
                'at2': 'val2',
                'at3': 'val3'
            },
            'events': [self.history_creator._create_event('created'), self.history_creator._create_event('deleted')]
        })

        new_item = Item({
            'key': '1',
            'link': 'http://fake.url',
            'attributes': {
                'at1': 'val1',
                'at2': 'val2_v2',
                'at3': 'val3'
            },
            'events': [self.history_creator._create_event('created')]
        })

        new_items = {'1': new_item}
        old_items = {'1': old_item}

        new_items = self.history_creator.process(new_items, old_items)

        self.assertEqual(1, len(new_items))
        self.assertTrue('1' in new_items)
        item = new_items['1']
        self.assertEqual(2, len(item.events))
        self.assertEqual('created', item.events[0].text)
        self.assertEqual('at2 from val2 to val2_v2', item.events[1].text)

    def test_update_prcess_no_updates(self):
        old_item = Item({
            'key': '1',
            'link': 'http://fake.url',
            'attributes': {
                'at1': 'val1',
                'at2': 'val2',
                'at3': 'val3'
            },
            'events': [self.history_creator._create_event('created')]
        })

        new_item = Item({
            'key': '1',
            'link': 'http://fake.url',
            'attributes': {
                'at1': 'val1',
                'at2': 'val2',
                'at3': 'val3'
            }
        })

        new_items = {'1': new_item}
        old_items = {'1': old_item}

        new_items = self.history_creator.process(new_items, old_items)

        self.assertEqual(1, len(new_items))
        self.assertTrue('1' in new_items)
        item = new_items['1']
        self.assertEqual(1, len(item.events))
        self.assertEqual('created', item.events[0].text)
        self.assertFalse(item.is_new)
        self.assertFalse(item.is_deleted)
        self.assertFalse(item.is_updated)

    def test_update_prcess_deleted_item_no_redeletion(self):
        item = Item({
            'key': '1',
            'link': 'http://fake.url',
            'attributes': {},
            'events': [
                self.history_creator._create_event('created'),
                self.history_creator._create_event('deleted')
            ]
        })

        items = {}
        items = self.history_creator.process(
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
        self.assertFalse(item.is_deleted)
        self.assertFalse(item.is_new)
        self.assertFalse(item.is_updated)
