import unittest
from qgis.core import QgsCoordinateReferenceSystem, QgsPointXY, QgsCoordinateTransform


class TestUtils(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.WGS = QgsCoordinateReferenceSystem.fromEpsgId(4326)
        cls.PSEUDO = QgsCoordinateReferenceSystem.fromEpsgId(3857)

    def test_dummy(self):
        self.assertEqual(1, 1)
