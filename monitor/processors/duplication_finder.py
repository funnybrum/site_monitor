from re import sub

from monitor.deduplicator.description import DescriptionBasedDeduplicator
from monitor.deduplicator.image import ImageBasedDeduplicator
from monitor.models.item import Item, Event


class DuplicationFinder(object):
    def __init__(self, config):
        self.config = config

    def process(self, items):
        """
        Create list of items containing only unique items with updates. Or to say it with another words - the result
        does not contain items that doesn't have updates. Also the result contain just single item for all duplicated
        items with updates.

        Note: all is_ flags will be set to False after the method returns.

        :param items: the items to be deduplicated.
        :return: deduplicated item dict.
        """

        self._fill_in_deduplication_data(items)
        return self._create_deduplicated_items(items)

    def _fill_in_deduplication_data(self, items):
        deduplicators = [ImageBasedDeduplicator(), DescriptionBasedDeduplicator()]
        for item in items.values():
            for deduplicator in deduplicators:
                deduplicator.fill_in_dedup_data(item)

    def _create_deduplicated_items(self, items):
        """ Create list containg only items with updates with merged history for each item. """

        deduplicated_items_with_updates = []

        # TODO - Not very efficient mechanism for finding duplicates. Find a way to make it faster.
        def is_duplicate():
            # Check if the item and the other_item are duplicate. Accomplished by verifying if they have common
            # deduplication key.
            return not set(item.deduplicate_keys).isdisjoint(other_item.deduplicate_keys)

        # Iterate over all items
        for item in items.values():

            duplicate_item_keys = set()
            # Iterate over all items once again looking for duplicates
            for other_item in items.values():
                if is_duplicate():
                    duplicate_item_keys.add(other_item.key)

            duplicate_items = [items[key] for key in duplicate_item_keys]

            if any(i.is_new or i.is_updated or i.is_deleted for i in duplicate_items):
                # So we have an item with update. Create deduplication item for visualisation purposes.
                result_item = Item()
                deduplicated_items_with_updates.append(result_item)

                result_item.key = duplicate_items[0].key
                result_item.link = duplicate_items[0].link
                result_item.attributes = duplicate_items[0].attributes
                result_item.is_new = any(i.is_new for i in duplicate_items)
                result_item.is_updated = any(i.is_updated for i in duplicate_items)
                result_item.is_deleted = any(i.is_deleted for i in duplicate_items)

                # Set all is_ flags to False to avoid multiple inclusion of the same item in the resulting list.
                for it in duplicate_items:
                    it.is_new = False
                    it.is_updated = False
                    it.is_deleted = False

                result_item.events = []
                for it in duplicate_items:
                    for ev in it.events:
                        result_item.events.append(Event({
                            'datetime': ev.datetime,
                            'text': '<a href="%s">*</a> %s' % (it.link, ev.text)
                        }))

                result_item.events.sort(key=lambda x: x.datetime)

                self._extract_min_max_price(result_item)
                result_item.all_links = set([it.link for it in duplicate_items])

                # Keep only useful updates and remove all non-interesting. There are currently a lot of deleted and
                # re-created events currently that are of no interest.
                result_item.events = [ev for ev in result_item.events if 'price' in ev.text or
                                                                         'description' in ev.text or
                                                                         'created' in ev.text]

        return deduplicated_items_with_updates

    def _extract_min_max_price(self, item):
        # Go over all updates and try to extract min and max price.
        def accumulate_price(price_text, min_p, max_p):
            price_text = sub(r'\D', '', price_text)
            if not price_text:
                return min_p, max_p

            price = int(price_text)

            if not min_p or min_p > price:
                min_p = price

            if not max_p or max_p < price:
                max_p = price

            return min_p, max_p

        min_price = None
        max_price = None

        for event in item.events:
            start_index = event.text.index('">') + 2
            end_index = event.text.index('</a>')
            text = event.text[start_index:end_index]
            if 'price from ' in text:
                old_price_text, new_price_text = text.replace('price from ', '').split(' to ')
                min_price, max_price = accumulate_price(old_price_text, min_price, max_price)
                min_price, max_price = accumulate_price(new_price_text, min_price, max_price)

        item.min_price = min_price
        item.max_price = max_price
