from collections import defaultdict


EMPTY_SET = set()


class CompositeDeduplicator(object):
    """
    Composite de-duplicator. Combine image and description based de-duplication in one
    de-duplicator.

    Not fully implemented.
    """

    def __init__(self, deduplicators):
        self.deduplicatos = deduplicators

    def get_duplicates(self, items):
        dedup_keys = defaultdict(set)

        for deduplicator in self.deduplicatos:
            dedup_data = deduplicator.get_duplicates(items)
            for duplicate_items in dedup_data.values():
                keys = set([item.key for item in duplicate_items])

                all_keys = set(keys)
                for key in keys:
                    all_keys = all_keys | dedup_keys.get(key, EMPTY_SET)

                for key in all_keys:
                    dedup_keys[key] = all_keys

                for item in duplicate_items:
                    dedup_keys[item.key] = keys

        result = defaultdict(list)
        for keys in dedup_keys.values():

            one_key = next(iter(keys))
            if one_key in result:
                # we've already processed this keyset
                continue

            duplicates = [items[k] for k in keys]
            for key in keys:
                result[key] = duplicates

        return result


if __name__ == '__main__':
    from monitor.storage.shelve import ShelveStorage
    from monitor.deduplicator.image import ImageBasedDeduplicator
    from monitor.deduplicator.description import DescriptionBasedDeduplicator
    items = ShelveStorage('prop_gm.db.db').load()
    print 'Loaded %s items' % len(items)
    dedup_dic = CompositeDeduplicator([ImageBasedDeduplicator(), DescriptionBasedDeduplicator()]).get_duplicates(items)

    for key, value in dedup_dic.items():
        if len(value) > 1:
            print 'Duplicates detected on the following URLs'
            for item in value:
                print item.link

    print 'Got %s unique items' % len([len(v) for v in dedup_dic.values() if len(v) > 1])
    print 'Got %s items total' % sum(len(v) for v in dedup_dic.values() if len(v) > 1)

