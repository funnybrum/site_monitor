from monitor.config.loader import ConfigLoader
from monitor.storage.shelve import ShelveStorage
from simplediff import html_diff

"""
Perform clean up on the events. Remove re-created events and price updates with no actual price update.
"""


def db_update(storage):
    db = storage.load()

    for key, item in db.iteritems():
        new_events = []
        for i in range(0, len(item.events)):
            event = item.events[i]
            if 'created' in event.text and i > 0:
                # Skip all created (and re-created) events except the first one.
                continue

            if 'deleted' in event.text and i < len(item.events) - 1:
                # Skip all delete events except the last one.
                continue

            if 'price from' in event.text:
                old_price_text, new_price_text = event.text.replace('price from ', '').split(' to ')
                diff = html_diff(old_price_text, new_price_text)
                if '<del>' not in diff and '<del>' not in diff:
                    # Difference is in spaces, the update can be skipped.
                    continue

            new_events.append(event)

        item.events = new_events

    storage.save(db)


if __name__ == '__main__':
    configs = ConfigLoader.load_all_configs()
    for config in configs:
        storage = ShelveStorage(config.database)
        db_update(storage)

    print 'Done.'
