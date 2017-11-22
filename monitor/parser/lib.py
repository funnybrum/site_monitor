from urlparse import (
    urlparse,
    parse_qs
)

from monitor.common.log import log


def amazon_id_extractor(value):
    """
    Amazon item IDs are encoded as part of the URL. The URL itself is not consistent and can't be used as ID. This
    method extracts the ID value by assuming that it is surrounded by '/dp/' and '/ref='.
    """
    start = value.find('%2Fdp%2F')
    end = value.find('%2Fref%3D')
    start_len = 8

    if start == -1:
        start = value.find('/dp/')
        end = value.find('/ref=')
        start_len = 4

    value = value[start + start_len:end]
    if len(value) != 10:
        log('Got properly incorrect ID for Amazon.com item - %s' % value)
    return value


def amazon_link_extractor(value):
    """
    The Amazon.com item links are part of a query argument of the extracted URL. This extract the real URL and remove
    all non-relevant details.
    """
    qs = urlparse(value).query
    url = parse_qs(qs).get('url', [None])[0]
    if not url:
        url = value
    url = url[0:url.find('/ref=')]
    return url

def trim(value):
    return value.replace('\n', '').lstrip().rstrip()
