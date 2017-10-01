import re

MAX_PAGES = 100

FAKE_IMAGE_MATCHERS = [
    re.compile('.*images/s.jpg.*'),
    re.compile('.*photo_small.gif.*'),
    re.compile('.*photo_med.gif.*')]
