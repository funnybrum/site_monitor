from __future__ import absolute_import

import shelve
from os.path import join

from monitor.models.item import Item
from monitor import DATABASE_FOLDER


class ShelveStorage(object):
    def __init__(self, filename):
        self.filename = join(DATABASE_FOLDER, 'v2_%s' % filename)

    def save(self, data):
        """
        Save the data to the shelve file.

        :param data: dict, key is string key, value is Item models.
        """
        # Writeback is false by intention. If an error is hit while serializing the database will not be destroyed.
        db = shelve.open(self.filename, writeback=False)
        db.clear()

        for key, model in data:
            db[key] = model.to_primitive()

        db.close()

    def load(self):
        """
        Loads the stored items.
        :return: dict, with Item model values. Keys are the item keys.
        """
        result = {}
        db = shelve.open(self.filename, writeback=False)

        for key, value in db:
            result[key] = Item(value)

        db.close()

        return result