from datetime import datetime
from re import sub

from models.item import Event
from notifier.renderer import HTMLGenerator
from notifier.sender import EMail
from parser.parser import Parser
from storage.shelve import ShelveStorage
from common.log import log


class Processor(object):
    def __init__(self, config, params={}):
        self.config = config
        self.params = params
        self.storage = ShelveStorage(config.database)
        self.messages = []

    def execute(self):
        if not self.config.enabled:
            return

        current_items = self.get_current_items()
        saved_items = self.storage.load()

        self.update(current_items, saved_items)

        new_count = len([i for i in current_items.values() if i.is_new])
        updated_count = len([i for i in current_items.values() if i.is_updated])
        deleted_count = len([i for i in current_items.values() if i.is_deleted])

        should_send_notification =\
            (self.config.send_new and new_count > 0) \
            or (self.config.send_updates and updated_count > 0) \
            or (self.config.send_deletes and deleted_count > 0)

        log('Finished with %s, got %s new, %s updated, %s removed.' %
            (self.config.name, new_count, updated_count, deleted_count))

        notification_body = HTMLGenerator(self.config).generate(current_items.values(), self.messages)

        # a few lines of debug code ...
        # with open('/tmp/monitor.html', 'w') as out_file:
        #     out_file.write(notification_body.encode('UTF-8'))

        if should_send_notification and not self.params.get('dry_run', False):
            log('Sending email for %s to %s' % (self.config.name, self.config.smtp.recipient))
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
                    if self.config.tracked_properties and attribute_key not in self.config.tracked_properties:
                        continue

                    if self._are_value_different(old_item.attributes[attribute_key],
                                                 item.attributes[attribute_key],
                                                 attribute_key):
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

    def _are_value_different(self, old, new, key):
        """
        Compare old and new attribute values. For all attributes except for the price the comparison is direct. For
        the price additional logic is considered.

        :param old:
        :param new:
        :param key:
        :return: True if they are considered different, False otherwise
        """

        if self.config.name != 'Amazon.com':
            return old != new

        if key != 'price':
            return old != new

        # Amazon, price comparison. If difference is less than 1% or less than 5 - consider values the same.
        old = float(sub('[^\d.]+', '', old))
        new = float(sub('[^\d.]+', '', new))
        if 0.9 < old/new < 1.1 or abs(old-new) < 5:
            return False

        return True


# if __name__ == '__main__':
#     from monitor.config.loader import ConfigLoader
#     configs = ConfigLoader.load_all_configs()
#     config = [c for c in configs if c.name == 'Amazon.com'][0]
#     Processor(config, {'dry_run': True}).execute()
