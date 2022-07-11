# -*- coding: utf-8 -*-

from .ui import get_ui_class

from qgis.PyQt.QtWidgets import QWidget
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtWidgets import QSpinBox
from qgis.PyQt.QtWidgets import QCheckBox
from qgis.core import QgsWkbTypes
from qgis.core import QgsProject
from qgis.core import QgsVectorLayer
from qgis.gui import QgsMapLayerComboBox


import os.path

FORM_CLASS = get_ui_class(os.path.dirname(__file__), 'compute_tsp.ui')


class DlgProcessLightnings(QDialog, FORM_CLASS):
    """
    Dialog to select the layers and parameters to calculate the path of the lightnings route
    """

    cbo_layer_lightnings: QgsMapLayerComboBox
    cbo_layer_helicopter: QgsMapLayerComboBox
    spn_max_distance: QSpinBox
    spn_eps: QSpinBox
    chk_enable_grouping: QCheckBox

    def __init__(self, parent: QWidget = None) -> None:
        """
        Constructor.
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        # Create the exclusion list of non-conforming layers
        no_point_layers = list()
        for layer in QgsProject.instance().mapLayers().values():
            if layer.geometryType() != QgsWkbTypes.PointGeometry:
                no_point_layers.append(layer)
        # Add the list to the widgets to exclude the non-conforming layers
        self.cbo_layer_lightnings.setExceptedLayerList(no_point_layers)
        self.cbo_layer_helicopter.setExceptedLayerList(no_point_layers)
        # Set default values and parameters to the widgets
        self.spn_max_distance.setMinimum(0)
        self.spn_max_distance.setMaximum(9999)
        self.spn_eps.setMinimum(0)
        self.spn_eps.setMaximum(9999)
        self.spn_eps.setDisabled(True)
        self.chk_enable_grouping.setChecked(False)
        # Create the event handlers for the UI responses
        self.chk_enable_grouping.stateChanged.connect(self.__on_grouping_changed)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908

    def __on_grouping_changed(self) -> None:
        """
        Event handler to respond to the creation of cluster enable or disable click event.
        """
        self.spn_eps.setDisabled(not self.chk_enable_grouping.isChecked())

    @property
    def lightnings_layer(self) -> QgsVectorLayer:
        return self.cbo_layer_lightnings.currentLayer()

    @property
    def helicopter_layer(self) -> QgsVectorLayer:
        return self.cbo_layer_helicopter.currentLayer()

    @property
    def helicopter_maximum_distance(self) -> int:
        return self.spn_max_distance.value()

    @helicopter_maximum_distance.setter
    def helicopter_maximum_distance(self, value: int):
        self.spn_max_distance.setValue(value)

    @property
    def grouping_eps(self) -> int:
        return self.spn_eps.value()

    @grouping_eps.setter
    def grouping_eps(self, value: int):
        self.spn_eps.setValue(value)

    @property
    def enable_lightning_grouping(self) -> bool:
        return self.chk_enable_grouping.isChecked()

    @enable_lightning_grouping.setter
    def enable_lightning_grouping(self, value: bool):
        self.chk_enable_grouping.setChecked(value)
