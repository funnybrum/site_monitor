#!/usr/bin/env python
# encoding: utf-8
import urllib2
import shelve
import time
import multiprocessing
import datetime

from lib.common import log
from lxml import etree
from lib.email import send_email
from jinja2 import Environment, PackageLoader

DB_PATH = './database/'
TEMPLATE_PATH = './templates/'
DEFAULT_TEMPLATE = 'base_v3.html'
DEFAULT_SUBJECT = 'Properties monitor update'

DEFAULT_PAGE = 1
PAGE_SIZE = 20


class Processor(multiprocessing.Process):

    def __init__(self, config, dry_run, show_html):
        self.config_name = config.get('name')
        self.db_file = DB_PATH + config.get('database')
        self.template_name = config.get('template_name', DEFAULT_TEMPLATE)
        self.recipient = config.get('recipient')
        self.dry_run = dry_run
        self.show_html = show_html
        self.enabled = config.get('enabled', True)
        self.sites = config.get('sites', {})
        self.template_config = config.get('template_config', {})
        self.subject = config.get('subject', DEFAULT_SUBJECT)
        self.smtp_config = config.get('smtp')
        return super(Processor, self).__init__()

    def _process_site(self, site_name, site_config):
        log("Running for %s" % site_name)

        result = {}
        if not site_config.get('enabled', True):
            return result

        encoding = site_config.get('encoding')
        list_items_xpath = site_config.get('list_items_match', [])
        item_attributes = site_config.get('item_attributes', [])
        search_url = site_config.get('search_url', None)
        max_pages_match = site_config.get('max_pages_match')
        max_pages_count = site_config.get('max_pages_count')

        max_pages = (max_pages_count or
                     self._get_max_pages(search_url, max_pages_match, encoding) or
                     PAGE_SIZE)

        for page_num in xrange(0, max_pages):
            url = search_url.format(page_num + 1)
            tree = self._get_html_tree(url, encoding)
            list_items = tree.xpath(list_items_xpath)
            if len(list_items) == 0:
                break
            for item in list_items:
                parsed = self._parse_item_attributes(item, item_attributes)
                if parsed:
                    result.update(parsed)
                else:
                    log('Failed to parse item in %s' % site_name)

        return result

    def run(self):
        log("Create a processor %s" % self.config_name)

        if not self.enabled:
            return

        results = {}

        for site_name, site_config in self.sites.iteritems():
            site_results = self._process_site(site_name, site_config)
            log('Got %s items for %s' % (len(site_results), site_name))
            results.update(site_results)

        db = shelve.open(self.db_file)
        removed, updated, new = self._filter_result(results, db)
        log("Processor %s - %s removed, %s updated, %s new" % (self.config_name, len(removed), len(updated), len(new)))

        if len(new) or len(updated):
            html = self._render_html(
                {
                    "config": self.template_config,
                    "site_config": site_config,
                    "data": {
                        "removed": {},
                        "updated": updated,
                        "new": new,
                    },
                    "as_of": datetime.datetime.now()
                })
            if self.show_html:
                log(html)

            if not self.dry_run:
                send_email(self.subject, html, self.recipient, self.smtp_config)
            log("Email sent to %s for %s" % (self.recipient, self.config_name))

        db.close()

    def _parse_item_attributes(self, item_element, item_attributes):
        result = {}
        id_value = self._get_id(item_element, item_attributes)
        if not id_value:
            return
        for item in item_attributes:
            value = item_element.xpath(item['match'])
            if not isinstance(value, list):
                value = [value]
            value = [v.strip() for v in value if v.strip()]
            value = [item.get('prefix', '') + v + item.get('suffix', '') for v in value]
            result.update({item['name']: value})
        return {id_value: result}

    def _filter_result(self, current_data, db):
        removed = {}
        new = {}
        updated = {}

        for key in set(db.keys() + current_data.keys()):
            if key in db and key in current_data:
                if db[key]['price'] != current_data[key]['price']:
                    updated[key] = current_data[key]
                    if 'old_prices' not in updated[key]:
                        updated[key]['old_prices'] = []
                    updated[key]['old_prices'].append({"date": datetime.datetime.now(),
                                                       "price": db[key]['price']})
                    db[key] = current_data[key]
            elif key in db and 'deleted_at' not in db[key]:
                removed[key] = db[key]
                removed[key]['deleted_at'] = time.time()
                db[key] = removed[key]
            elif key in current_data:
                new[key] = current_data[key]
                db[key] = current_data[key]

        return removed, updated, new

    def _get_id(self, item_element, item_attributes):
        id_match = None
        for item in item_attributes:
            if item['name'] == 'id':
                id_match = item['match']
                break
        if not id_match:
            raise KeyError('Missing required "id" item attribute!')

        id_value = item_element.xpath(id_match)
        return id_value[0] if id_value else None

    def _render_html(self, properties):
        env = Environment(loader=PackageLoader('prop_monitor', 'templates'))
        template = env.get_template(self.template_name)
        return template.render(properties)

    def _get_max_pages(self, search_url, max_pages_match, encoding=None):
        if not search_url or not max_pages_match:
            return

        url = search_url.format(DEFAULT_PAGE)
        tree = self._get_html_tree(url, encoding)
        max_pages = None
        try:
            max_pages_str = tree.xpath(unicode(max_pages_match))
            if isinstance(max_pages_str, list):
                max_pages_str = max_pages_str[0]
            max_pages = int(max_pages_str)
        except:
            log("Unable to determine max pages for %s" % url)
        return max_pages

    def _get_html_tree(self, url, encoding=None):
        html = urllib2.urlopen(url).read()
        parser = None
        if encoding:
            parser = etree.HTMLParser(encoding=encoding)
        return etree.HTML(html, parser=parser)


if __name__ == '__main__':
    from lib.yaml_config import load_configs
    configs = load_configs('./config/')
    for i in configs:
        if 'name' in i and i['name'] == 'Car monitor':
            config = i

    Processor(config=config, dry_run=False, show_html=False).run()
