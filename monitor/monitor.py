from datetime import datetime

from models.item import Event
from notifier.renderer import HTMLGenerator
from notifier.sender import EMail
from parser.parser import Parser
from storage.shelve import ShelveStorage
from common.log import log


class Monitor(object):
    def __init__(self, config):
        self.config = config
        self.storage = ShelveStorage(config.database)
        self.messages = []

    def execute(self):
        if not self.config.enabled:
            return

        current_items = self.get_current_items()
        saved_items = self.storage.load()

        self.update(current_items, saved_items)

        notification_body = HTMLGenerator(self.config).generate(current_items.values(), self.messages)
        EMail(self.config.smtp).send(notification_body)
        self.storage.save(current_items)

    def get_current_items(self):
        """
        Process the configured sites and return dict of items.
        """
        current_items = {}

        for site in self.config.sites:
            if not site.enabled:
                continue

            parser = Parser(site, self.config.headers)
            items = parser.process()
            current_items.update(items)
            msg = 'Processed %s, got %s items' % (site.name, len(items))
            self.messages.append(msg)
            log(msg)

        return current_items

    def update(self, current_items, saved_items):
        """
        Update the current items with details from the old items. This includes creating and setting the event history,
        annotating the current items as new/updated/deleted and keeping the deleted items.
        :return: nothing is returned. The updates are applied over the current items dict.
        """

        for item in current_items.values() + saved_items.values():
            item.is_deleted = False
            item.is_new = False
            item.is_updated = False

        for key, item in current_items.items():

            if key not in saved_items:
                # New item detected, fill in the 'created' event.
                item.events = [self._create_event('created')]
                item.is_new = True
            else:
                old_item = saved_items[key]

                # Existing item, transfer the history
                item.events = old_item.events

                if item.events[-1].text == 'deleted':
                    item.events.append(self._create_event('re-created'))

                # Check for update on attributes and update the history
                for attribute_key in item.attributes.keys():
                    if item.attributes[attribute_key] != old_item.attributes[attribute_key]:
                        item.is_updated = True
                        item.events.append(self._create_event(
                            '%s from %s to %s' % (
                                attribute_key,
                                old_item.attributes[attribute_key],
                                item.attributes[attribute_key])

                        ))

        for key in set(saved_items.keys()) - set(current_items.keys()):
            current_items[key] = saved_items[key]

            if current_items[key].events[-1].text != 'deleted':
                current_items[key].events.append(self._create_event('deleted'))
                current_items[key].is_deleted = True

    def _create_event(self, text):
        return Event({
            'datetime': datetime.now(),
            'text': text
        })
