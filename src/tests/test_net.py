from hermpy.net import ClientMESSENGER


def test_messenger_instruments():
    client = ClientMESSENGER()
    keys = client.FILE_PATTERN.keys()

    mag_items = ["MAG", "MAG 1s", "MAG 5s", "MAG 10s", "MAG 60s"]
    assert all(item in keys for item in mag_items)

    fips_items = ["FIPS"]
    assert all(item in keys for item in fips_items)
