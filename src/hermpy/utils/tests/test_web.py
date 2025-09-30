import unittest

import requests

from hermpy.utils import Urls


class Test_Web_Access(unittest.TestCase):
    def test_PDS_BASE(self):
        r = requests.head(Urls.PDS_BASE)
        self.assertEqual(r.status_code, 200)


if __name__ == "__main__":
    unittest.main()
