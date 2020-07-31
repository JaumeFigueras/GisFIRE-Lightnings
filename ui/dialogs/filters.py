from .ui import get_ui_class

from qgis.PyQt.QtWidgets import QDialog
from qgis.core import QgsWkbTypes
from qgis.core import QgsProject

import os.path

FORM_CLASS = get_ui_class(os.path.dirname(__file__), 'filters.ui')
class DlgFilterLightnings(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        no_point_layers = list()
        for layer in QgsProject.instance().mapLayers().values():
            if layer.geometryType() != QgsWkbTypes.PointGeometry:
                no_point_layers.append(layer)
        self._layer.setExceptedLayerList(no_point_layers)
        self._enable_positive_filter.setChecked(True)
        self._enable_positive_current_filter.setChecked(False)
        self._enable_positive_min_current_filter.setDisabled(True)
        self._enable_positive_min_current_filter.setChecked(False)
        self._double_positive_min_current_filter.setDisabled(True)
        self._double_positive_min_current_filter.setMinimum(0)
        self._double_positive_min_current_filter.setMaximum(9999)
        self._enable_positive_max_current_filter.setDisabled(True)
        self._enable_positive_max_current_filter.setChecked(False)
        self._double_positive_max_current_filter.setDisabled(True)
        self._double_positive_max_current_filter.setMinimum(0)
        self._double_positive_max_current_filter.setMaximum(9999)
        self._enable_positive_filter.stateChanged.connect(self.onEnablePositiveFilterChanged)
        self._enable_positive_current_filter.stateChanged.connect(self.onEnablePositiveCurrentFilterChanged)
        self._enable_positive_min_current_filter.stateChanged.connect(self.onEnablePositiveMinCurrentFilterChanged)
        self._enable_positive_max_current_filter.stateChanged.connect(self.onEnablePositiveMaxCurrentFilterChanged)
        self._enable_negative_filter.setChecked(True)
        self._enable_negative_current_filter.setChecked(False)
        self._enable_negative_min_current_filter.setDisabled(True)
        self._enable_negative_min_current_filter.setChecked(False)
        self._double_negative_min_current_filter.setDisabled(True)
        self._double_negative_min_current_filter.setMinimum(0)
        self._double_negative_min_current_filter.setMaximum(9999)
        self._enable_negative_max_current_filter.setDisabled(True)
        self._enable_negative_max_current_filter.setChecked(False)
        self._double_negative_max_current_filter.setDisabled(True)
        self._double_negative_max_current_filter.setMinimum(0)
        self._double_negative_max_current_filter.setMaximum(9999)
        self._enable_negative_filter.stateChanged.connect(self.onEnableNegativeFilterChanged)
        self._enable_negative_current_filter.stateChanged.connect(self.onEnableNegativeCurrentFilterChanged)
        self._enable_negative_min_current_filter.stateChanged.connect(self.onEnableNegativeMinCurrentFilterChanged)
        self._enable_negative_max_current_filter.stateChanged.connect(self.onEnableNegativeMaxCurrentFilterChanged)
        self._enable_cloud_filter.setChecked(False)

    def onEnablePositiveFilterChanged(self):
        self._enable_positive_current_filter.setDisabled(not self._enable_positive_filter.isChecked())
        if self._enable_positive_filter.isChecked():
            self._enable_positive_min_current_filter.setDisabled(not self._enable_positive_current_filter.isChecked())
            self._enable_positive_max_current_filter.setDisabled(not self._enable_positive_current_filter.isChecked())
            if self._enable_positive_current_filter.isChecked():
                self._double_positive_min_current_filter.setDisabled(not self._enable_positive_min_current_filter.isChecked())
                self._double_positive_max_current_filter.setDisabled(not self._enable_positive_max_current_filter.isChecked())
            else:
                self._double_positive_min_current_filter.setDisabled(True)
                self._double_positive_max_current_filter.setDisabled(True)
        else:
            self._enable_positive_min_current_filter.setDisabled(True)
            self._enable_positive_max_current_filter.setDisabled(True)
            self._double_positive_min_current_filter.setDisabled(True)
            self._double_positive_max_current_filter.setDisabled(True)

    def onEnablePositiveCurrentFilterChanged(self):
        self._enable_positive_min_current_filter.setDisabled(not self._enable_positive_current_filter.isChecked())
        self._enable_positive_max_current_filter.setDisabled(not self._enable_positive_current_filter.isChecked())
        if self._enable_positive_current_filter.isChecked():
            self._double_positive_min_current_filter.setDisabled(not self._enable_positive_min_current_filter.isChecked())
            self._double_positive_max_current_filter.setDisabled(not self._enable_positive_max_current_filter.isChecked())
        else:
            self._double_positive_min_current_filter.setDisabled(True)
            self._double_positive_max_current_filter.setDisabled(True)

    def onEnablePositiveMinCurrentFilterChanged(self):
        self._double_positive_min_current_filter.setDisabled(not self._enable_positive_min_current_filter.isChecked())

    def onEnablePositiveMaxCurrentFilterChanged(self):
        self._double_positive_max_current_filter.setDisabled(not self._enable_positive_max_current_filter.isChecked())

    def onEnableNegativeFilterChanged(self):
        self._enable_negative_current_filter.setDisabled(not self._enable_negative_filter.isChecked())
        if self._enable_negative_filter.isChecked():
            self._enable_negative_min_current_filter.setDisabled(not self._enable_negative_current_filter.isChecked())
            self._enable_negative_max_current_filter.setDisabled(not self._enable_negative_current_filter.isChecked())
            if self._enable_negative_current_filter.isChecked():
                self._double_negative_min_current_filter.setDisabled(not self._enable_negative_min_current_filter.isChecked())
                self._double_negative_max_current_filter.setDisabled(not self._enable_negative_max_current_filter.isChecked())
            else:
                self._double_negative_min_current_filter.setDisabled(True)
                self._double_negative_max_current_filter.setDisabled(True)
        else:
            self._enable_negative_min_current_filter.setDisabled(True)
            self._enable_negative_max_current_filter.setDisabled(True)
            self._double_negative_min_current_filter.setDisabled(True)
            self._double_negative_max_current_filter.setDisabled(True)

    def onEnableNegativeCurrentFilterChanged(self):
        self._enable_negative_min_current_filter.setDisabled(not self._enable_negative_current_filter.isChecked())
        self._enable_negative_max_current_filter.setDisabled(not self._enable_negative_current_filter.isChecked())
        if self._enable_negative_current_filter.isChecked():
            self._double_negative_min_current_filter.setDisabled(not self._enable_negative_min_current_filter.isChecked())
            self._double_negative_max_current_filter.setDisabled(not self._enable_negative_max_current_filter.isChecked())
        else:
            self._double_negative_min_current_filter.setDisabled(True)
            self._double_negative_max_current_filter.setDisabled(True)

    def onEnableNegativeMinCurrentFilterChanged(self):
        self._double_negative_min_current_filter.setDisabled(not self._enable_negative_min_current_filter.isChecked())

    def onEnableNegativeMaxCurrentFilterChanged(self):
        self._double_negative_max_current_filter.setDisabled(not self._enable_negative_max_current_filter.isChecked())
