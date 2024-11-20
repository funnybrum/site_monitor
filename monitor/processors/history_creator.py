from simplediff import html_diff
from datetime import datetime
from re import sub

from monitor.models.item import Event


class HistoryCreator(object):

    def __init__(self, config):
        self.config = config

    def _populate_the_is_flags(self, item):
        item.is_new = False
        item.is_updated = False
        item.is_deleted = False

    def _process_item(self, old_item, new_item):
        """
        Create event history based on the old and new item details. The even history include details like:
          * create/delete events
          * price change events
          * description change events

        The result is returned in a new monitor.models.item.Item object. It will contain a few attributes providing
        additional details:
          * is_new - True iff the item is a new item. False otherwise.
          * is_deleted - True iff the item is a deleted item. False otherwise.
          * is_updated - True iff the item is an updated item. False otherwise.

        :param old_item: the old item, can be None
        :param new_item: the new item, can be None
        :return: monitor.models.item.Item fully populated object with a few additional properties.
        """
        if old_item is None and new_item is None:
            raise ValueError('Can\'t create history without items')

        if old_item is None:
            new_item.events = [self._create_event('created')]
            self._populate_the_is_flags(new_item)
            new_item.is_new = True
            return new_item

        if new_item is None:
            self._populate_the_is_flags(old_item)
            if old_item.events[-1].text != 'deleted':
                old_item.events.append(self._create_event('deleted'))
                old_item.is_deleted = True
            return old_item

        new_item.events = old_item.events
        new_item.deduplicate_keys = old_item.deduplicate_keys
        new_item.deduplicate_metadata = old_item.deduplicate_metadata
        self._populate_the_is_flags(new_item)

        if new_item.events[-1].text == 'deleted':
            # Re-created item. We have two options:
            # 1) Add a bunch of deleted/re-created events. Seems to be not so useful.
            # 2) Remove the deleted event.
            # 1 proved to be not so useful for quite some time. Let's go with option 2.
            new_item.events = new_item.events[:-1]
            
        # Check for update on attributes and update the history
        for attribute_key in new_item.attributes.keys():
            if self.config.tracked_properties and attribute_key not in self.config.tracked_properties:
                # Not a property that is being tracked. Don't check for updates over it.
                continue

            different, event_text = self._are_value_different(old_item.attributes[attribute_key],
                                                              new_item.attributes[attribute_key],
                                                              attribute_key)

            if different:
                new_item.is_updated = True
                new_item.events.append(self._create_event(event_text))

        return new_item

    def _create_event(self, text):
        return Event({
            'datetime': datetime.now(),
            'text': text
        })

    def _are_value_different(self, old, new, key):
        """
        Compare old and new attribute values. For all attributes except for the price the comparison is direct. For
        the price additional logic is considered.

        :param old:
        :param new:
        :param key:
        :return: (True/False indicating if the values are different, text to be used for the event update if old != new)
        """

        if self.config.name in ['Amazon.com', 'Amazon.co.uk'] and key == 'price':
            old_price = float(sub('[^\d.]+', '', old))
            new_price = float(sub('[^\d.]+', '', new))
            different = not (0.98 < old_price / new_price < 1.02 or abs(old_price - new_price) < 5)
            return different, '%s from %s to %s' % (key, old, new)

        if key == 'description':
            old = old if old else ""
            new = new if new else ""
            diff = html_diff(old, new)
            if '<del>' in diff or '<del>' in diff:
                return True, diff
            else:
                return False, None

        return old != new, '%s from %s to %s' % (key, old, new)

    def process(self, current_items, saved_items):
        """
        Create updated list of items based on the current_items (the new items) and the saved items (the items loaded
        from the DB).

        :param current_items: Dict of current items (the one that were parsed from the sites). Shouldn't have historical
                              data (like events) attached.
        :param saved_items: Dict of items loaded from the DB. Should contain full historical data (i.e. the events).
        :return: Dict containing all items (old and new) with fully populated history.
        """
        result = {}
        for key in set(current_items.keys() + saved_items.keys()):
            old_item = saved_items.get(key, None)
            new_item = current_items.get(key, None)
            result[key] = self._process_item(old_item, new_item)

        return result
