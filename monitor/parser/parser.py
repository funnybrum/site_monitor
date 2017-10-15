import urllib2
import chardet
from lxml import etree

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
            for page_num in xrange(0, self.config.max_pages or MAX_PAGES):

                new_items_found = False

                page_url = url.format(page_num)
                tree = self._get_html_tree(page_url)
                list_items = tree.xpath(self.config.items_x_path)

                for item in list_items:
                    item = self._process_item(item)

                    if item:
                        if item.key not in items:
                            new_items_found = True
                            items[item.key] = item
                    else:
                        log(u'Failed to parse item in %s' % self.config.name)

                if not new_items_found and page_num > 1:
                    break

        return items

    def _get_html_tree(self, url):
        req = urllib2.Request(url, headers=self.headers)
        html = urllib2.urlopen(req).read()
        html_encoding = chardet.detect(html)['encoding']
        html = html.decode(html_encoding).encode('utf-8')
        parser = etree.HTMLParser(encoding='utf-8')
        return etree.HTML(html, parser=parser)

    def _process_item(self, item_tree):
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

            # Temporary workaround for Amazon.com items that fail to parse.
            if 'Amazon.com' == self.config.name:
                if not value or len(value) < 4:
                    return None

            if item_property.post_processor is not None:
                post_processor = getattr(lib, item_property.post_processor)
                value = post_processor(value)

            if value is not None:
                # Sanity check. In some cases the prefix is already applied. I.e. in case of URLs. Some sites have links
                # to external sites for subset of the items and in that case no prefix should be added.
                if item_property.prefix and not value.startswith(item_property.prefix[:4]):
                    value = item_property.prefix + value

                if item_property.suffix:
                    value = value + item_property.suffix

                # Check for 'blank' images. If such are detected - remove the image link value.
                if 'image' == item_property.name:
                    if any([r.match(value) for r in FAKE_IMAGE_MATCHERS]):
                        value = ''
            else:
                print u'Got %s for %s for %s at %s' % (value, item_property.name, item.key, self.config.name)

            if 'id' == item_property.name:
                item.key = value
            elif 'link' == item_property.name:
                item.link = value
            else:
                item.attributes[item_property.name] = value

        return item
