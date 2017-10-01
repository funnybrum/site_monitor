from unittest import TestCase

from test import TEST_CONFIG_FOLDER

from monitor.config.loader import ConfigLoader


class LoaderTest(TestCase):
    def test_config_discovery(self):
        configs = ConfigLoader.load_all_configs(TEST_CONFIG_FOLDER)
        self.assertEqual(3, len(configs))
        self.assertTrue('test config 1' in [c.name for c in configs])
        self.assertTrue('test config 2' in [c.name for c in configs])

    def test_smtp_config_parsing(self):
        configs = ConfigLoader.load_all_configs(TEST_CONFIG_FOLDER)
        cfg = configs[0] if configs[0].name == 'test config 1' else configs[1]
        self.assertIsNotNone(cfg.smtp)
        self.assertEquals('username', cfg.smtp.username)
        self.assertEquals('password', cfg.smtp.password)
        self.assertEquals('na@na.na', cfg.smtp.recipient)
        self.assertEquals('test subject', cfg.smtp.subject)
        self.assertEquals('sender_text', cfg.smtp.sender)
        self.assertEquals('smtp.gmail.com', cfg.smtp.server)
        self.assertEquals(587, cfg.smtp.port)

    def test_site_config_parsing(self):
        configs = ConfigLoader.load_all_configs(TEST_CONFIG_FOLDER)
        cfg = configs[0] if configs[0].name == 'test config 1' else configs[1]
        self.assertEquals(3, len(cfg.sites))
        self.assertEquals(3, len(set([site.name for site in cfg.sites])))
        site = None
        for s in cfg.sites:
            if s.name == 'site 1':
                site = s

        self.assertEquals(True, site.enabled)
        self.assertEquals(1, len(site.urls))
        self.assertEquals('https://foo.bar/path', site.urls[0])
        self.assertEqual(1, site.max_pages)
        self.assertEquals("id('dp-container')", site.items_x_path)
        self.assertEquals(2, len(site.item_properties))
        self.assertEquals(set(['id', 'price']), set([p.name for p in site.item_properties]))

    def test_config(self):
        configs = ConfigLoader.load_all_configs(TEST_CONFIG_FOLDER)
        for config in configs:
            config.validate()
