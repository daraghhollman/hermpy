from hermpy.net import ClientMESSENGER
from hermpy.utils import download_files


def test_messenger_instruments():
    client = ClientMESSENGER()
    keys = client.FILE_PATTERN.keys()

    mag_items = ["MAG", "MAG 1s", "MAG 5s", "MAG 10s", "MAG 60s"]
    assert all(item in keys for item in mag_items)

    fips_items = ["FIPS"]
    assert all(item in keys for item in fips_items)


TEST_URLS = [
    "http://spiftp.esac.esa.int/data/SPICE/BEPICOLOMBO/kernels/aareadme.txt",
    "http://spiftp.esac.esa.int/data/SPICE/BEPICOLOMBO/misc/BEPICOLOMBO.html",
    "http://spiftp.esac.esa.int/data/SPICE/JUICE/misc/JUICE.html",
]


def test_downloads():
    """Ensure files can be fetched one at a time"""
    files = download_files(TEST_URLS)
    assert len(files) == len(TEST_URLS)
    assert all(files)
