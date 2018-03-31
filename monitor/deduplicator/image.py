from PIL import Image
from StringIO import StringIO
import urllib2

from monitor.common.constants import FAKE_IMAGE_MATCHERS
from monitor.deduplicator.base import DeduplicatorBase


class ImageBasedDeduplicator(DeduplicatorBase):
    """
    Extract de-duplication keys based on item images.
    """
    def __init__(self):
        pass

    def _extract_dedup_key(self, item, image_key='image'):
        if image_key not in item.attributes or not item.attributes[image_key]:
            return None

        if any([r.match(item.attributes[image_key]) for r in FAKE_IMAGE_MATCHERS]):
            return None

        try:
            image_data = StringIO(urllib2.urlopen(item.attributes[image_key]).read())
            image = Image.open(image_data)
            return self.dhash(image)
        except:
            print 'Failed to load image %s from %s' % (item.attributes[image_key], item.link)

        return None

    def dhash(self, image, hash_size=8):
        """
        Extract image hash. Based on https://blog.iconfinder.com/detecting-duplicate-images-using-python-cb240b05a3b6.
        """
        # Grayscale and shrink the image in one step.
        image = image.convert('L').resize(
            (hash_size + 1, hash_size),
            Image.ANTIALIAS,
        )

        # Compare adjacent pixels.
        difference = []
        for row in xrange(hash_size):
            for col in xrange(hash_size):
                pixel_left = image.getpixel((col, row))
                pixel_right = image.getpixel((col + 1, row))
                difference.append(pixel_left > pixel_right)

        # Convert the binary array to a hexadecimal string.
        decimal_value = 0
        hex_string = []
        for index, value in enumerate(difference):
            if value:
                decimal_value += 2 ** (index % 8)
            if (index % 8) == 7:
                hex_string.append(hex(decimal_value)[2:].rjust(2, '0'))
                decimal_value = 0

        return ''.join(hex_string)

    def fill_in_dedup_data(self, item, image_key='image'):
        if any([r.match(str(item.attributes[image_key])) for r in FAKE_IMAGE_MATCHERS]):
            return

        if item.deduplicate_metadata is None:
            item.deduplicate_metadata = []

        if item.attributes[image_key] in item.deduplicate_metadata:
            # de-dup data is already extracted for that image
            return

        item.deduplicate_metadata.append(item.attributes[image_key])
        super(ImageBasedDeduplicator, self).fill_in_dedup_data(item)


if __name__ == '__main__':
    from monitor.storage.shelve import ShelveStorage
    items = ShelveStorage('properties.db').load()
    dedup_dic = ImageBasedDeduplicator().procecss(items)
    for key, value in dedup_dic.items():
        if len(value) > 1:
            print 'Duplicates detected on the following URLs'
            for item in value:
                print item.link

    print 'Got %s unique items' % len([len(v) for v in dedup_dic.values() if len(v) > 1])
    print 'Got %s items total' % sum(len(v) for v in dedup_dic.values() if len(v) > 1)
