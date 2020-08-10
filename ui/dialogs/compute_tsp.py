from .ui import get_ui_class

from qgis.PyQt.QtWidgets import QDialog
from qgis.core import QgsWkbTypes
from qgis.core import QgsProject

import os.path

FORM_CLASS = get_ui_class(os.path.dirname(__file__), 'compute_tsp.ui')
class DlgProcessLightnings(QDialog, FORM_CLASS):
    """Dialog to select the layers and parameters to calculate the path of the
    lightnings route
    """

    def __init__(self, parent=None):
        """Constructor."""
        QDialog.__init__(self, parent)
        self.setupUi(self)
        # Create the exclusion list of non conforming layers
        no_point_layers = list()
        for layer in QgsProject.instance().mapLayers().values():
            if layer.geometryType() != QgsWkbTypes.PointGeometry:
                no_point_layers.append(layer)
        # Add the list to the widgets to exclude the non conforming layers
        self._layer_lightnings.setExceptedLayerList(no_point_layers)
        self._layer_helicopter.setExceptedLayerList(no_point_layers)
        # Set default values and parameters to the widgets
        self._max_distance.setMinimum(0)
        self._max_distance.setMaximum(9999)
        self._eps.setMinimum(0)
        self._eps.setMaximum(9999)
        self._eps.setDisabled(True)
        self._enable_grouping.setChecked(False)
        # Create the event handlers for the UI responses
        self._enable_grouping.stateChanged.connect(self.onGroupingChanged)

    def onGroupingChanged(self):
        """Event handler to respond to the creation of cluster enable or disable
        click event.
        """
        self._eps.setDisabled(not self._enable_grouping.isChecked())

    @property
    def lightnings_layer(self):
        return self._layer_lightnings.currentLayer()

    @property
    def helicopter_layer(self):
        return self._layer_helicopter.currentLayer()

    @property
    def helicopter_maximum_distance(self):
        return self._max_distance.value()

    @helicopter_maximum_distance.setter
    def helicopter_maximum_distance(self, value):
        self._max_distance.setValue(value)

    @property
    def grouping_eps(self):
        return self._eps.value()

    @grouping_eps.setter
    def grouping_eps(self, value):
        self._eps.setValue(value)

    @property
    def enable_lightning_grouping(self):
        return self._enable_grouping.isChecked()

    @enable_lightning_grouping.setter
    def enable_lightning_grouping(self, value):
        self._enable_grouping.setChecked(value)
