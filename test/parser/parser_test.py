from unittest import TestCase

from test import my_vcr, TEST_CONFIG_FOLDER

from monitor.parser.parser import Parser
from monitor.config.loader import ConfigLoader


class ParserTest(TestCase):
    @my_vcr.use_cassette('test_parser_holmes_bg.yaml')
    def test_parser_holmes_bg(self):
        """
        Verifies:
          1) The iteration stops on page number 7 (there are only 7 pages recorded in the cassette)
          2) All items are parsed (72)
          3) The automatic encoding detection works (the page is cp-1251)
        """
        configs = ConfigLoader.load_all_configs(TEST_CONFIG_FOLDER)
        holmes_cfg = [cfg for cfg in configs if cfg.name == 'test_holmes_bg'][0]
        parser = Parser(holmes_cfg.sites[0], holmes_cfg.headers)

        items = parser.process()
        self.assertEqual(72, len(items))

    @my_vcr.use_cassette('test_parser_holmes_bg_with_missing_elements.yaml')
    def test_parser_holmes_bg_with_missing_elements(self):
        """
        Uses manually patched cassette.
        Verifies:
            1) Page iteration stops after the first page with no items
            2) Missing image is not causing failure (this was a bug)
            3) Missing elements are properly parsed as 'None'
        """
        configs = ConfigLoader.load_all_configs(TEST_CONFIG_FOLDER)
        holmes_cfg = [cfg for cfg in configs if cfg.name == 'test_holmes_bg'][0]
        parser = Parser(holmes_cfg.sites[0], holmes_cfg.headers)

        items = parser.process()
        self.assertEqual(1, len(items))

        item = items.values()[0]
        self.assertIsNone(item.attributes['image'])
        self.assertTrue('0878426911' in item.attributes['description'])
        self.assertEquals('http://www.holmes.bg/pcgi/home.cgi?act=3&adv=1j150408486382722', item.link)
        self.assertEquals('/pcgi/home.cgi?act=3&adv=1j150408486382722', item.key)

    @my_vcr.use_cassette('test_parser_holmes_bg_with_redundant_prefix.yaml')
    def test_parser_holmes_bg_with_redundant_prefix(self):
        """
        Uses manually patched cassette.
        Verifies:
            1) Prefix is skipped if the value that should be prefixed already contains it.
        """
        configs = ConfigLoader.load_all_configs(TEST_CONFIG_FOLDER)
        holmes_cfg = [cfg for cfg in configs if cfg.name == 'test_holmes_bg'][0]
        parser = Parser(holmes_cfg.sites[0], holmes_cfg.headers)

        items = parser.process()
        self.assertEqual(1, len(items))

        item = items.values()[0]
        self.assertEquals('http://www.holmes.bg/pcgi/home.cgi?act=3&adv=1j150408486382722', item.link)

    # TODO add tests for:
    # 1) validators, it should also cover the case when the
    # 2) required properties
