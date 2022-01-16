import unittest

from qgis.PyQt.QtTest import QTest
from qgis.PyQt.QtCore import Qt, QEvent, QPoint, QTimer
from qgis.PyQt.QtWidgets import QPushButton, QDialogButtonBox, QMessageBox, QApplication
from qgis.gui import QgsMapCanvas, QgsMapMouseEvent
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsRectangle, QgsVectorLayer, QgsFeature, \
    QgsFeatureIterator

from .utilities import get_qgis_app

# 1. Get all relevant QGIS objects
CANVAS: QgsMapCanvas
QGISAPP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestFlow(unittest.TestCase):
    def test_full_failure(self):
        """Test failing request"""

        # 3. first set up a project
        CRS = QgsCoordinateReferenceSystem.fromEpsgId(3857)
        project = QgsProject.instance()
        CANVAS.setExtent(QgsRectangle(258889, 7430342, 509995, 7661955))
        CANVAS.setDestinationCrs(CRS)

        # 4. Create and open the dialog
        # dlg = QuickApiDialog(IFACE)
        # dlg.open()
        self.assertTrue(True)
