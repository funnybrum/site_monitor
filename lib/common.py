import sys
from datetime import datetime

premailer_timeout = 10


def log(message):
    """ Log message to stdout with time prefix. """
    timestamp = datetime.now().strftime('[%d/%m/%y %H:%M:%S]')
    print u'%s %s' % (timestamp, message)
    sys.stdout.flush()
