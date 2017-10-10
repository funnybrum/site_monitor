from collections import defaultdict


class DeduplicatorBase(object):

    def procecss(self, items):
        dedup_dict = defaultdict(list)
        for item in items.values():
            key = self._extract_dedup_key(item)
            if key:
                dedup_dict[key].append(item)

        return dedup_dict

    def _convert_result(self):
        pass