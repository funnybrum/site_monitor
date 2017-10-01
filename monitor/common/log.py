import sys
from datetime import datetime


def log(message):
    """ Log message to stdout with time prefix. """
    timestamp = datetime.now().strftime('[%d/%m/%y %H:%M:%S]')
    print u'%s %s' % (timestamp, message)
    sys.stdout.flush()
