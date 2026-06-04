from astropy.utils.data import download_file, download_files_in_parallel

from hermpy.net import ClientMESSENGER
from hermpy.utils.os import get_multiprocessing_start_method


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


def test_astropy_download_sequential():
    """Ensure files can be fetched one at a time"""
    paths = [download_file(url, pkgname="hermpy", cache=True) for url in TEST_URLS]
    assert len(paths) == len(TEST_URLS)
    assert all(paths)


def test_astropy_download_parallel():
    """Ensure parallel download works"""
    paths = download_files_in_parallel(
        TEST_URLS,
        pkgname="hermpy",
        cache=True,
        multiprocessing_start_method=get_multiprocessing_start_method(),
    )
    assert len(paths) == len(TEST_URLS)
    assert all(paths)
