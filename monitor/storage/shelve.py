from __future__ import absolute_import

import shelve
from os.path import join, isdir
from os import makedirs
from json import loads, dumps

from monitor.models.item import Item
from monitor import DATABASE_FOLDER


class ShelveStorage(object):
    def __init__(self, filename):
        if (not isdir(DATABASE_FOLDER)):
            makedirs(DATABASE_FOLDER)
        self.filename = join(DATABASE_FOLDER, '%s' % filename)
        

    def save(self, data):
        """
        Save the data to the shelve file.

        :param data: dict, key is string key, value is Item models.
        """
        # Writeback is false by intention. If an error is hit while serializing the database will not be destroyed.
        db = shelve.open(self.filename, writeback=False)
        db.clear()

        for key, model in data.items():
            db[key] = dumps(model.to_primitive())

        db.close()

    def load(self):
        """
        Loads the stored items.
        :return: dict, with Item model values. Keys are the item keys.
        """
        result = {}
        db = shelve.open(self.filename, writeback=False)

        for key, value in db.items():
            result[key] = Item(loads(value))

        db.close()

        return result