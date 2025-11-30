import math
import os
import unittest
import urllib.request
from pathlib import Path

from sunpy.time import TimeRange
from tqdm import tqdm

from hermpy.mag import load_between_dates


class Test_Loading(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Download two example data files
        cls.download_dir = Path("./.tests/")

        if not cls.download_dir.exists():
            os.mkdir(cls.download_dir)

        urls = [
            "https://pds-ppi.igpp.ucla.edu/data/mess-mag-calibrated/data/mso/2011/091_120_APR/MAGMSOSCI11113_V08.TAB",
            "https://pds-ppi.igpp.ucla.edu/data/mess-mag-calibrated/data/mso/2011/091_120_APR/MAGMSOSCI11114_V08.TAB",
        ]
        paths = [cls.download_dir / url.split("/")[-1] for url in urls]
        for url, path in zip(urls, paths):
            # If the path already exists, we don't need to re-download.
            if path.exists():
                continue

            download_with_progress_bar(url, path)

    def test_single_file_loading(self):
        """
        Test if we can load a file of data
        """

        data = load_between_dates(
            self.download_dir,
            TimeRange("2011-04-23 12:00", "2011-04-23 13:00"),
            average=None,  # Testing full res data
        )

        # Check length is correct
        assert len(data) == 71992

        # Just check the first row
        r = data.iloc[0]

        # Check aberration angle
        assert math.isclose(r["Aberration Angle"], 0.098313, abs_tol=0.000001)

        # Check position was aberrated
        assert math.isclose(r["X MSM' (radii)"], 1.19386, abs_tol=0.00001)

        # Check position was converted from MSO to MSM
        assert math.isclose(r["Z MSM (radii)"], -6.53362, abs_tol=0.00001)
        assert math.isclose(r["Z MSM' (radii)"], -6.53362, abs_tol=0.00001)

        # Check MAG is correct
        assert math.isclose(r["Bx'"], -5.65442, abs_tol=0.00001)

        # This data is missing, and should throw an error
        with self.assertRaises(FileNotFoundError):
            load_between_dates(
                self.download_dir,
                TimeRange("2011-06-23 12:00", "2011-06-23 13:00"),
                average=None,  # Testing full res data
            )

    def test_loading_across_files(self):
        data = load_between_dates(
            self.download_dir,
            TimeRange("2011-04-23 12:00", "2011-04-24 12:00"),
            average=None,  # Testing full res data
        )

        assert len(data) == 1727902


def download_with_progress_bar(url: str, path: Path) -> None:
    """
    Downloads file from url: str to path: Path with a progress bar.
    """

    response = urllib.request.urlopen(url)
    file_size = int(response.getheader("Content-Length").strip())

    with (
        open(path, "wb") as file,
        tqdm(
            desc=f"Downloading: {url.split('/')[-1]}",
            total=file_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar,
    ):
        while True:
            chunk = response.read(1024)
            if not chunk:
                break

            file.write(chunk)
            bar.update(len(chunk))


if __name__ == "__main__":
    unittest.main()
