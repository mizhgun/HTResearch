# stdlib imports
import unittest

# project imports
from HTResearch.Utilities.geocoder import geocode


class LoggingUtilityTest(unittest.TestCase):

    def test_geocoding(self):
        addr = "4444 Browning Pl, Lincoln, NE, 68516"
        check = [40.7485215, -96.6579318]
        lat_long = geocode(addr)

        self.assertEqual(lat_long, check)


if __name__ == '__main__':
    unittest.main()