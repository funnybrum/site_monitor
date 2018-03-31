from collections import defaultdict


class DeduplicatorBase(object):

    def get_duplicates(self, items):
        """
        Extract de-duplication data.

        :param items: items to extract de-duplication data for.
        :return: dict result, key is de-duplication key, value is list of items that are considered as duplicate.
        """
        dedup_dict = defaultdict(list)
        for item in items.values():
            key = self._extract_dedup_key(item)
            if key:
                dedup_dict[key].append(item)

        return dedup_dict

    def get_duplicate_item_keys(self, items):
        """
        Extract de-duplication keys.

        :param items: items to extract de-duplication keys for.
        :return: dict result, key is the item key, value is set of duplicate item keys.
        """
        dedup_keys = self.get_duplicates(items)

        result = {}
        for duplicate_items in dedup_keys.values():
            duplicate_keys = set([item.key for item in duplicate_items])
            for duplicate_key in duplicate_keys:
                result[duplicate_key] = duplicate_keys

        return result

    def fill_in_dedup_data(self, item):
        if item.deduplicate_keys is None:
            item.deduplicate_keys = []

        dedup_key = self._extract_dedup_key(item)

        if dedup_key and dedup_key not in item.deduplicate_keys:
            item.deduplicate_keys.append(dedup_key)
