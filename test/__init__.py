from os.path import dirname, join
import vcr

my_vcr = vcr.VCR(
    cassette_library_dir=join(dirname(__file__), 'resources/cassettes'),
    record_mode='once'
)

TEST_CONFIG_FOLDER = join(dirname(__file__), 'resources/test_config')
