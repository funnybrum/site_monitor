from schematics.models import Model
from schematics.types import (
    StringType,
    DictType,
    ListType,
    URLType,
    ModelType,
    DateTimeType
)


class Event(Model):
    """
    Represent events associated with the item. Examples are:
     * create
     * delete
     * property value change
    """
    datetime = DateTimeType(required=True)

    text = StringType(required=True)


class Item(Model):
    """
    Represent single item found by the monitor.
    """
    # item key, should be unique
    key = StringType(required=True)

    # link to the item
    link = URLType(required=True)

    # all other item attributes like price and description
    attributes = DictType(StringType, required=False)

    events = ListType(ModelType(Event), required=True)

    def is_empty(self):
        """
        Return True iff all properties are set to None.
        """
        return\
            self.key is None\
            and self.link is None\
            and (
                self.attributes is None
                or not any(self.attributes.values()))
