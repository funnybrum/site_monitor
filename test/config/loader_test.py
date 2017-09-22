from unittest import TestCase

from monitor.config.loader import ConfigLoader


class LoaderTest(TestCase):
    def test_config_discovery(self):
        configs = ConfigLoader.load_all_configs('test/resources/test_config')
        self.assertEqual(2, len(configs))
        self.assertTrue('test config 1' in [c.name for c in configs])
        self.assertTrue('test config 2' in [c.name for c in configs])

    def test_smtp_config_parsing(self):
        configs = ConfigLoader.load_all_configs('test/resources/test_config')
        cfg = configs[0] if configs[0].name == 'test config 1' else configs[1]
        self.assertIsNotNone(cfg.smtp)
        self.assertEquals('username', cfg.smtp.username)
        self.assertEquals('password', cfg.smtp.password)
        self.assertEquals('na@na.na', cfg.smtp.recipient)
        self.assertEquals('test subject', cfg.smtp.subject)

    def test_site_config_parsing(self):
        configs = ConfigLoader.load_all_configs('test/resources/test_config')
        cfg = configs[0] if configs[0].name == 'test config 1' else configs[1]
        self.assertEquals(3, len(cfg.sites))
        self.assertEquals(3, len(set([site.name for site in cfg.sites])))
        site = None
        for s in cfg.sites:
            if s.name == 'site 1':
                site = s

        self.assertEquals(True, site.enabled)
        self.assertEquals('utf-8', site.encoding)
        self.assertEquals(1, len(site.urls))
        self.assertEquals('https://url/1', site.urls[0])
        self.assertEqual(1, site.max_pages)
        self.assertEquals("id('dp-container')", site.items_x_path)
        self.assertEquals(2, len(site.item_properties))
        self.assertEquals(set(['id', 'price']), set([p.name for p in site.item_properties]))

