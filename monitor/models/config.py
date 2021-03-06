from schematics.models import Model
from schematics.types import (
    BooleanType,
    StringType,
    IntType,
    DictType,
    ListType,
    ModelType
)


class ItemProperty(Model):
    # property name
    name = StringType(required=True)

    # x path
    x_path = StringType(required=True)

    # prefix to be added in front of the extracted value
    prefix = StringType(required=False, default='')

    # sufix to be appended to the end of the extracted value
    suffix = StringType(required=False, default='')

    # indicate if the property is URL, used for data validation
    is_url = BooleanType(required=False, default=False)

    # post processing method that can transform the extracted result
    post_processor = StringType(required=False, default=None)

    # regex that validates if the value is correct
    validator = StringType(required=False, default=None)


class Site(Model):
    # name of the site
    name = StringType(required=True)

    # search URLs
    urls = ListType(StringType, required=True)

    # True or False - indicates if the config is enabled, default is True
    enabled = BooleanType(required=False, default=True)

    # items_x_path
    items_x_path = StringType(required=True)

    # maximum number of pages to be processed
    max_pages = IntType(required=False, default=0)

    # item properties, instances of ItemProperties
    item_properties = ListType(ModelType(ItemProperty))

    # list of properties that must have values
    required_properties = DictType(BooleanType, default=None)


class SMTPConfig(Model):
    recipient = StringType(required=True)
    sender = StringType(required=True)
    username = StringType(required=True)
    password = StringType(required=True)
    subject = StringType(required=True)
    server = StringType(required=True)
    port = IntType(required=True)


class Config(Model):
    # True or False - indicates if the config is enabled, default is True
    enabled = BooleanType(required=False, default=True)

    # name of the config
    name = StringType(required=True)

    # database file name
    database = StringType(required=True)

    # True if new items should be send
    send_new = BooleanType(required=False, default=True)

    # True if updated items should be send
    send_updates = BooleanType(required=False, default=True)

    # True if deleted items should be send
    send_deletes = BooleanType(required=False, default=True)

    # headers to be included in http requests
    headers = DictType(StringType, required=False)

    # Site list
    sites = ListType(ModelType(Site), required=True)

    # list of properties to track updates on
    tracked_properties = ListType(StringType, default=None)

    # SMTP config
    smtp = ModelType(SMTPConfig, required=True)

    template = StringType(required=True)
    template_config = DictType(StringType, required=False, default={})
