from monitor.config.loader import ConfigLoader
from monitor.storage.shelve import ShelveStorage
from simplediff import html_diff


def db_update(storage):
    db = storage.load()

    for key, item in db.iteritems():
        new_events = []
        for event in item.events:
            if 'description from ' in event.text:
                old_text = event.text
                old_description, new_description = event.text.replace('description from ', '').split(' to ')
                event.text = 'description: ' + html_diff(old_description, new_description)

                if '<del>' in event.text or '<del>' in event.text:
                    new_events.append(event)
            else:
                new_events.append(event)

            item.events = new_events

    storage.save(db)


if __name__ == '__main__':
    configs = ConfigLoader.load_all_configs()
    for config in configs:
        storage = ShelveStorage(config.database)
        db_update(storage)

    print 'Done.'
