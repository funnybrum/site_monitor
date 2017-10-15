import yaml
import os

from monitor import CONFIG_FOLDER

from monitor.models.config import (
    Site,
    ItemProperty,
    Config,
    SMTPConfig
)


class ConfigLoader(object):
    @classmethod
    def load_config(cls, file_name):
        config_dict = ConfigLoader._load_yaml(file_name)

        config = Config()
        config.enabled = config_dict.get('enabled', config.enabled)
        config.name = config_dict['name']
        config.database = config_dict['database']
        config.send_new = config_dict.get('send_new', config.send_new)
        config.send_updates = config_dict.get('send_updates', config.send_updates)
        config.send_deletes = config_dict.get('send_deletes', config.send_deletes)
        config.headers = config_dict.get('headers', {})
        config.sites = []
        config.template = config_dict.get('template', None)
        config.template_config = config_dict.get('template_config', {})
        for site_name, site_config in config_dict.get('sites', {}).items():
            site = cls._parse_site_config(site_name, site_config)
            config.sites.append(site)

        smtp_config = SMTPConfig()
        smtp_config.recipient = config_dict['recipient']
        smtp_config.subject = config_dict['subject']
        smtp_config.username = config_dict['smtp']['user']
        smtp_config.password = config_dict['smtp']['password']
        smtp_config.server = config_dict['smtp']['server']
        smtp_config.port = config_dict['smtp']['port']
        smtp_config.sender = config_dict['smtp']['sender']

        config.smtp = smtp_config

        return config

    @classmethod
    def _parse_site_config(cls, name, config):
        site = Site()

        site.name = name
        site.enabled = config['enabled']
        site.items_x_path = config['list_items_match']
        site.max_pages = config.get('max_pages_count', site.max_pages)
        if 'search_url' in config:
            site.urls = [config['search_url']]
        else:
            site.urls = [i['url'] for i in config['search_urls']]
        site.item_properties = []
        for property_config in config['item_attributes']:
            property = cls._parse_item_property(property_config)
            site.item_properties.append(property)

        return site

    @classmethod
    def _parse_item_property(cls, config):
        property = ItemProperty()
        property.name = config['name']
        property.x_path = config['match']
        property.prefix = config.get('prefix', property.prefix)
        property.suffix = config.get('suffix', property.suffix)
        property.is_url = config.get('is_url', property.is_url)
        property.post_processor = config.get('post_processor', property.post_processor)
        return property

    @classmethod
    def _load_yaml(cls, file_name):
        """
        Read a yaml file into dict
        :param file_name: Load config from yaml file with specified name.
        :return: dict
        """
        with open(file_name, 'r') as config_file:
            config = yaml.load(config_file)

        if 'extend' in config:
            parent_file = os.path.dirname(file_name) + os.path.sep + config['extend']
            parent_config = cls._load_yaml(parent_file)
            cls._merge_config_dicts(config, parent_config)
            del config['extend']

        return config

    @classmethod
    def _merge_config_dicts(cls, dict1, dict2, path=None):
        """merges dict2 into dict1"""
        if path is None:
            path = []
        for key in dict2:
            if key in dict1:
                if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                    # sub-dict properties, merge them
                    cls._merge_config_dicts(dict1[key], dict2[key], path + [str(key)])
                else:
                    # dict1 property takes precedence
                    pass
            else:
                dict1[key] = dict2[key]
        return dict1

    @classmethod
    def load_all_configs(cls, configs_path=CONFIG_FOLDER):
        configs = []
        files = [os.path.join(configs_path, f)
                 for f in os.listdir(configs_path)
                 if os.path.isfile(os.path.join(configs_path, f)) and 'secrets.yaml' not in f]

        for file_name in files:
            configs.append(cls.load_config(file_name))
        return configs
