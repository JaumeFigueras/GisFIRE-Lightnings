# -*- coding: utf-8 -*-

from .ui import get_ui_class
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtWidgets import QComboBox
from qgis.gui import QgsMapLayerComboBox
from qgis.gui import QgsFieldComboBox
from qgis.core import QgsProject
from qgis.core import QgsWkbTypes
from qgis.core import QgsMapLayer
from qgis.core import QgsVectorLayer
from qgis.core import QgsFeature

import os.path

from typing import List
from typing import Set
from typing import Any

FORM_CLASS = get_ui_class(os.path.dirname(__file__), 'urban_areas.ui')


class DlgUrbanAreas(QDialog, FORM_CLASS):
    """
    Dialog box to collect the layer, field and value that represent urban areas in a land cover area information layer

    TODO: Types
    """

    cbo_land_cover_layer: QgsMapLayerComboBox
    cbo_field: QgsFieldComboBox
    cbo_value: QComboBox
    values: Set[Any]

    def __init__(self, parent=None):
        """
        TODO

        :param parent:
        :type parent:
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        # Create the exclusion list of non-conforming layers
        no_polygon_layers: List[QgsMapLayer] = list()
        layer: QgsMapLayer
        for layer in QgsProject.instance().mapLayers().values():
            if layer.geometryType() != QgsWkbTypes.PolygonGeometry and layer.geometryType() != QgsWkbTypes.MultiPolygon:
                no_polygon_layers.append(layer)
        # Add the lists to the widget to exclude the non-conforming layers
        self.cbo_land_cover_layer.setExceptedLayerList(no_polygon_layers)
        self.cbo_land_cover_layer.layerChanged.connect(self.cbo_field.setLayer)
        self.cbo_field.fieldChanged.connect(self.__on_field_changed)
        layer: QgsVectorLayer = self.cbo_land_cover_layer.layer(0)
        self.cbo_field.setLayer(layer)
        self.values = set()

    def __on_field_changed(self):
        self.cbo_value.clear()
        self.values.clear()
        layer: QgsVectorLayer = self.cbo_land_cover_layer.currentLayer()
        attribute_name: str = self.cbo_field.currentField()
        if attribute_name is None or attribute_name == '':
            return
        feature: QgsFeature
        for feature in layer.getFeatures():
            value = feature.attribute(attribute_name)
            self.values.add(value)
        lst: List[str] = list(self.values)
        lst.sort()
        lst = [str(elem) for elem in lst]
        self.cbo_value.addItems(lst)

