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

import traceback
import sys

DB_PATH = './database/'
TEMPLATE_PATH = './templates/'
DEFAULT_TEMPLATE = 'base_v3.html'

DEFAULT_PAGE = 1
MAX_PAGES = 50


class Processor(multiprocessing.Process):
    def __init__(self, config, dry_run, show_html):
        self.config_name = config.get('name')
        self.db_file = DB_PATH + config.get('database')
        self.template_name = config.get('template_name', DEFAULT_TEMPLATE)
        self.recipients = config.get('recipient')
        if type(self.recipients) is not list:
            self.recipients = [self.recipients]
        self.dry_run = dry_run
        self.show_html = show_html
        self.enabled = config.get('enabled', True)
        self.sites = config.get('sites', {})
        self.template_config = config.get('template_config', {})
        self.subject = '%s %s' % (config.get('subject'), datetime.datetime.now().strftime("%d/%m/%Y"))
        self.smtp_config = config.get('smtp')
        self.send_new = config.get('send_new', True)
        self.send_updates = config.get('send_updates', True)
        self.send_deletes = config.get('send_deletes', True)
        self.headers = config.get('headers', {})
        return super(Processor, self).__init__()

    def _process_site(self, site_name, site_config):
        result = {}
        if not site_config.get('enabled', True):
            return result

        encoding = site_config.get('encoding')
        list_items_xpath = site_config.get('list_items_match', [])
        item_attributes = site_config.get('item_attributes', [])
        if site_config.get('search_urls', None):
            search_urls = {item['site'] : item['url'] for item in site_config.get('search_urls')}
        else:
            search_urls = {site_name: site_config.get('search_url')}

        for subsite_id, search_url in search_urls.iteritems():
            subsite_name = '%s - %s' % (site_name, subsite_id)
            subsite_result = {}

            for page_num in xrange(0, MAX_PAGES):
                url = search_url.format(page_num + 1)
                tree = self._get_html_tree(url, encoding)
                list_items = tree.xpath(list_items_xpath)
                if len(list_items) == 0 and page_num > 1:
                    break
                found_new_items = False
                for item in list_items:
                    parsed = self._parse_item_attributes(item, item_attributes)
                    if parsed:
                        if parsed.keys()[0] not in subsite_result:
                            found_new_items = True
                        subsite_result.update(parsed)
                    else:
                        log(u'Failed to parse item in %s' % site_name)
                if not found_new_items and page_num > 1:
                    break

            log('Processed %s pages for %s, got %s items' % (page_num, subsite_name, len(subsite_result)))
            result.update(subsite_result)

        return result

    def run(self):
        try:
            log(u'Create a processor %s' % self.config_name)

            if not self.enabled:
                return

            results = {}

            for site_name, site_config in self.sites.iteritems():
                site_results = self._process_site(site_name, site_config)
                results.update(site_results)

            db = shelve.open(self.db_file, writeback=False)
            removed, updated, new = self._filter_result(results, db)
            log(u'Processor %s - %s removed, %s updated, %s new' % (
                self.config_name, len(removed), len(updated), len(new)))

            if (len(new) and self.send_new) or \
                    (len(updated) and self.send_updates) or \
                    (len(removed) and self.send_deletes):
                html = self._render_html(
                    {
                        "config": self.template_config,
                        "site_config": site_config,
                        "data": {
                            "new": new if self.send_new else {},
                            "updated": updated if self.send_updates else {},
                            "removed": removed if self.send_deletes else {},
                        },
                        "as_of": datetime.datetime.now()
                    })
                if self.show_html:
                    log(html)

                if not self.dry_run:
                    for recipient in self.recipients:
                        send_email(self.subject, html, recipient, self.smtp_config)
                        log(u'Email sent to %s for %s' % (recipient, self.config_name))

            db.close()
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            log(u'Got exception while processing %s: %s' % (site_name, repr(e)))

    def _parse_item_attributes(self, item_element, item_attributes):
        result = {}
        id_value = self._get_id(item_element, item_attributes)
        if not id_value:
            return
        url_issue_detected = False
        for item in item_attributes:
            value = item_element.xpath(item['match'])
            if not isinstance(value, list):
                value = [value]
            prefix = item.get('prefix', '')
            suffix = item.get('suffix', '')
            value = [
                (prefix if not v.startswith(prefix[:4]) else '') +
                v.strip() +
                suffix for v in value
            ]

            if item['name'] in ['link', 'image'] and len(value) > 0:
                ref = value[0]
                if 'images/s.jpg' in ref or 'photo_small.gif' in ref or 'photo_med.gif' in ref:
                    pass
                elif ref.count('http') != 1 or ref.count('//') != 1:
                    url_issue_detected = True

            result.update({item['name']: value})

        if url_issue_detected:
            log('Detected a URL issue for %s -> %s' % (id_value, result))

        return {id_value: result}

    def _filter_result(self, current_data, db):
        removed = {}
        new = {}
        updated = {}

        for key in set(db.keys() + current_data.keys()):
            if key in db and key in current_data:
                diffs = self._get_diffs(old=db[key], new=current_data[key])
                if diffs:
                    current_data['key']['created_at'] = db[key]['created_at']
                    history = db[key]['history']
                    history = history + diffs
                    current_data[key]['history'] = history
                    db[key] = current_data[key]
                    updated[key] = db[key]
            elif key in db and 'deleted_at' not in db[key]:
                db[key]['deleted_at'] = time.time()
                removed[key] = db[key]
            elif key in current_data:
                current_data[key]['history'] = []
                current_data[key]['created_at'] = datetime.datetime.now()
                db[key] = current_data[key]
                new[key] = current_data[key]

        return removed, updated, new

    def _get_diffs(self, old, new):
        """
        Get list of diffs, list contains dicts with the following attributes:
          * key - key of attribute
          * old - old value
          * new - new value
          * date - modification date
        """
        diffs = []
        for key in set(new.keys()) - set(['link', 'image', 'description']):
            if old[key] != new[key]:
                diffs.append({
                    'key': key,
                    'old': old[key],
                    'new': new[key],
                    'date': datetime.datetime.now()
                })
        return diffs

    def _get_id(self, item_element, item_attributes):
        id_match = None
        for item in item_attributes:
            if item['name'] == 'id':
                id_match = item['match']
                break
        if not id_match:
            raise KeyError('Missing required "id" item attribute!')

        id_value = item_element.xpath(id_match)
        if type(id_value) is list:
            id_value = id_value[0]
        return id_value

    def _render_html(self, properties):
        env = Environment(loader=PackageLoader('prop_monitor', 'templates'))
        template = env.get_template(self.template_name)
        return template.render(properties)

    def _get_html_tree(self, url, encoding=None):
        # handler = urllib2.HTTPSHandler(debuglevel=1)
        # opener = urllib2.build_opener(handler)
        # urllib2.install_opener(opener)

        req = urllib2.Request(url, headers=self.headers)
        html = urllib2.urlopen(req).read()
        parser = None
        if encoding:
            parser = etree.HTMLParser(encoding=encoding)
        return etree.HTML(html, parser=parser)


if __name__ == '__main__':
    from lib.yaml_config import load_configs

    configs = load_configs('./config/')
    for i in configs:
        if 'name' in i and i['name'] == 'Properties monitor':
            config = i

    Processor(config=config, dry_run=True, show_html=False).run()
