from .ui import get_ui_class

from qgis.PyQt.QtWidgets import QDialog
from qgis.core import QgsWkbTypes
from qgis.core import QgsProject

import os.path

FORM_CLASS = get_ui_class(os.path.dirname(__file__), 'clipping.ui')
class DlgClipping(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        no_point_layers = list()
        no_polygon_layers = list()
        for layer in QgsProject.instance().mapLayers().values():
            if layer.geometryType() != QgsWkbTypes.PointGeometry:
                no_point_layers.append(layer)
            elif layer.geometryType() != QgsWkbTypes.PolygonGeometry and layer.geometryType() != QgsWkbTypes.MultiPolygon:
                no_polygon_layers.append(layer)
        self._layer_lightnings.setExceptedLayerList(no_point_layers)
        self._layer_polygons.setExceptedLayerList(no_polygon_layers)

    @property
    def lightnings_layer(self):
        return self._layer_lightnings.currentLayer()

    @property
    def polygons_layer(self):
        return self._layer_polygons.currentLayer()
