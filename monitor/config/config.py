class Config(object):
    def __init__(self):
        self.sites = []
        self.headers = {}

    # True or False - indicates if the config is enabled, default is True
    enabled = True

    # name of the config
    name = None

    # database file name
    database = None

    # True if new items should be send
    send_new = True

    # True if updated items should be send
    send_updates = True

    # True if deleted items should be send
    send_deletes = True

    # headers to be included in http requests
    headers = None

    # Site list
    sites = None

    # SMTP config
    smtp = None


class Site(object):
    def __init__(self):
        self.urls = []
        self.item_properties = []

    # name of the site
    name = None

    # encoding of the site pages, default is utf-8
    encoding = "utf-8"

    # search URLs
    urls = None

    # True or False - indicates if the config is enabled, default is True
    enabled = True

    # items_x_path
    items_x_path = None

    # item properties, instances of ItemProperties
    item_properties = None

    # maximum number of pages to be processed
    max_pages = 0


class ItemProperty(object):
    # property name
    name = None

    # x path
    x_path = None

    # prefix to be added in front of the extracted value
    prefix = ""

    # sufix to be appended to the end of the extracted value
    suffix = ""

    # indicate if the property is URL, used for data validation
    is_url = False

class SMTPConfig(object):
    username = None
    password = None
    recipient = None
    subject = None
