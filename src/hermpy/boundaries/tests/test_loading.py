"""
#######################################################################
As long as the Philpott crossing list remains only available via manual
download, we cannot reliably test these functionalities
#######################################################################

import unittest

import pandas

import hermpy.boundaries as boundaries
from hermpy.utils import User


class Test_Loading(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.philpott_crossings = boundaries.load_crossings(
            User.CROSSING_LISTS["Philpott"]
        )
        cls.philpott_crossings_no_data_gaps = boundaries.load_crossings(
            User.CROSSING_LISTS["Philpott"], include_data_gaps=False
        )

        cls.crossing_columns = [
            "Type",
            "Start Time",
            "Start MSO X (radii)",
            "Start MSO Y (radii)",
            "Start MSO Z (radii)",
            "Start MSO X (km)",
            "Start MSO Y (km)",
            "Start MSO Z (km)",
            "Start MSM X (radii)",
            "Start MSM Y (radii)",
            "Start MSM Z (radii)",
            "Start MSM X (km)",
            "Start MSM Y (km)",
            "Start MSM Z (km)",
            "End Time",
            "End MSO X (radii)",
            "End MSO Y (radii)",
            "End MSO Z (radii)",
            "End MSO X (km)",
            "End MSO Y (km)",
            "End MSO Z (km)",
            "End MSM X (radii)",
            "End MSM Y (radii)",
            "End MSM Z (radii)",
            "End MSM X (km)",
            "End MSM Y (km)",
            "End MSM Z (km)",
        ]

    def test_length(self):
        self.assertEqual(len(self.philpott_crossings), 16266)
        self.assertEqual(len(self.philpott_crossings_no_data_gaps), 16239)

    def test_type(self):
        self.assertIsInstance(self.philpott_crossings, pandas.DataFrame)
        self.assertIsInstance(self.philpott_crossings_no_data_gaps, pandas.DataFrame)

    def test_columns(self):
        self.assertEqual(
            self.philpott_crossings.columns.tolist(), self.crossing_columns
        )

    def test_backend(self):
        with self.assertRaises(ValueError):
            boundaries.load_crossings("Some/path", backend="something else")


if __name__ == "__main__":
    unittest.main()
"""
