import unittest
from qgis.core import QgsPointXY
from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()


class TestNominatim(unittest.TestCase):
    """
    Test that Nominatim is returning valid results.
    """

    def _assertCoordsAlmostEqual(self, pt1: QgsPointXY, pt2: QgsPointXY, places=6):
        """Assert coordinates are the same within 0.000005 degrees"""
        self.assertAlmostEqual(pt1.x(), pt2.x(), places=places)
        self.assertAlmostEqual(pt1.y(), pt2.y(), places=places)

    def test_success(self):
        in_pt = QgsPointXY(13.395317, 52.520174)

        self._assertCoordsAlmostEqual(in_pt, in_pt, places=4)

