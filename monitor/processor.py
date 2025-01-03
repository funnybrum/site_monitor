from notifier.renderer import HTMLGenerator
from notifier.sender import EMail
from parser.parser import Parser
from storage.shelve import ShelveStorage
from common.log import log
from monitor.processors.history_creator import HistoryCreator
from monitor.processors.duplication_finder import DuplicationFinder


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

        current_items = HistoryCreator(self.config).process(current_items, saved_items)

        new_count = len([i for i in current_items.values() if i.is_new])
        updated_count = len([i for i in current_items.values() if i.is_updated])
        deleted_count = len([i for i in current_items.values() if i.is_deleted])

        deduplicated_items = DuplicationFinder(self.config).process(current_items)

        should_send_notification =\
            (self.config.send_new and new_count > 0) \
            or (self.config.send_updates and updated_count > 0) \
            or (self.config.send_deletes and deleted_count > 0)

        log('Finished with %s, got %s new, %s updated, %s removed.' %
            (self.config.name, new_count, updated_count, deleted_count))

        notification_body = HTMLGenerator(self.config).generate(deduplicated_items, self.messages)

        # a few lines of debug code ...
        # with open('/brum/monitor.html', 'w') as out_file:
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


if __name__ == '__main__':
    from monitor.config.loader import ConfigLoader
    configs = ConfigLoader.load_all_configs()
    print([c.name for c in configs])
    configs = [c for c in configs if 'Vitara' in c.name]
    for config in configs:
        Processor(config, {'dry_run': False}).execute()
