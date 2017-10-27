import urllib2
import cchardet
import gzip
from lxml import etree
from StringIO import StringIO
from re import match, sub
from retrying import retry

from monitor.models.item import Item
from monitor.common.constants import MAX_PAGES, FAKE_IMAGE_MATCHERS
from monitor.common.log import log

from monitor.parser import lib


class Parser(object):
    def __init__(self, config, headers={}):
        self.config = config
        self.headers = headers

    def process(self):
        """
        Process the parser configuration and returns the results as models with type Item.

        :return: dict of items.
        """
        if not self.config.enabled:
            raise AssertionError('Configuraiton is not enabled.')

        items = {}

        for url in self.config.urls:
            max_pages = MAX_PAGES
            if self.config.max_pages != 0:
                self.config.max_pages + 1
            for page_num in xrange(1, max_pages):

                new_items_found = False

                page_url = url.format(page_num)
                try:
                    tree = self._get_html_tree(page_url)
                except Exception as e:
                    log(e.message)
                    log('Failed to get page %s, skipping' % page_url)
                    # This will stop iteration over the current URL pages
                    tree = etree.HTML('<html></html>')

                list_items = tree.xpath(self.config.items_x_path)

                for item in list_items:
                    item = self._parse_item(item)

                    if item:
                        if item.key not in items:
                            new_items_found = True
                            items[item.key] = item
                        else:
                            # Duplicate item, keep it only if the price is lower
                            try:
                                existing_price = float(sub('[^\d.]+', '', items[item.key].attributes['price']))
                                new_price = float(sub('[^\d.]+', '', item.attributes['price']))
                                if new_price < existing_price:
                                    items[item.key] = item
                            except (TypeError, ValueError, KeyError):
                                # In some cases there is no price or it is not a number.
                                continue

                if not new_items_found and page_num > 1:
                    break

        return items

    @retry(stop_max_attempt_number=5, wait_fixed=5000)
    def _get_html_tree(self, url):
        req = urllib2.Request(url, headers=self.headers)
        response = urllib2.urlopen(req)

        body = response.read()
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO(body)
            body = gzip.GzipFile(fileobj=buf).read()

        html_encoding = cchardet.detect(body)['encoding']
        html = body.decode(html_encoding).encode('utf-8')

        # # For debugging purposes
        # if 'amazon.com' in url:
        #     if not hasattr(self, 'page_count'):
        #         self.page_count = 0
        #     with open('/var/log/amazon_page_%s.html' % self.page_count, 'w') as out_f:
        #         out_f.write(html)
        #     print 'Page %s' % self.page_count
        #     self.page_count += 1

        parser = etree.HTMLParser(encoding='utf-8')
        return etree.HTML(html, parser=parser)

    def _parse_item(self, item_tree):
        item = Item()
        item.attributes = {}
        for item_property in self.config.item_properties:
            value = item_tree.xpath(item_property.x_path)
            if isinstance(value, list):
                if len(value) == 1:
                    value = value[0]
                elif len(value) > 1:
                    value = ', '.join(value)
                else:
                    # Nothing was matched, i.e. missing image for some item
                    value = None

            if value is not None:
                if item_property.post_processor is not None:
                    post_processor = getattr(lib, item_property.post_processor)
                    value = post_processor(value)

                # Sanity check. In some cases the prefix is already applied. I.e. in case of URLs. Some sites have links
                # to external sites for subset of the items and in that case no prefix should be added.
                if item_property.prefix and not value.startswith(item_property.prefix[:4]):
                    value = item_property.prefix + value

                if item_property.suffix:
                    value = value + item_property.suffix

                # Check for 'blank' images. If such are detected - remove the image link value.
                if 'image' == item_property.name:
                    if any([r.match(value) for r in FAKE_IMAGE_MATCHERS]):
                        value = None

            # If a property has validator - check it against the validator. If the value is not valid - don't set it.
            if item_property.validator:
                if value is None or not self.validate(value, item_property.validator):
                    continue

            self.set_property(item, item_property.name, value)

        if item.is_empty():
            return None

        if self.config.required_properties:
            for key, warning in self.config.required_properties.items():
                if self.get_property(item, key) is None:
                    if warning:
                        log('Failed to extract property %s, item = %s' % (key, item.to_primitive()))
                    return None

        return item

    def validate(self, value, validator):
        return value is not None and match(validator, value)

    def get_property(self, item, key):
        if 'id' == key:
            return item.key
        elif 'link' == key:
            return item.link
        else:
            return item.attributes.get(key)

    def set_property(self, item, key, value):
        if 'id' == key:
            item.key = value
        elif 'link' == key:
            item.link = value
        else:
            item.attributes[key] = value
