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
        self._layer.layerChanged.connect(self.onLayerSelected)
        self._enable_positive_filter.setChecked(True)
        self._enable_positive_current_filter.setChecked(True)
        self._enable_positive_min_current_filter.setDisabled(False)
        self._enable_positive_min_current_filter.setChecked(True)
        self._double_positive_min_current_filter.setDisabled(False)
        self._double_positive_min_current_filter.setMinimum(0)
        self._double_positive_min_current_filter.setMaximum(9999)
        self._enable_positive_max_current_filter.setDisabled(False)
        self._enable_positive_max_current_filter.setChecked(True)
        self._double_positive_max_current_filter.setDisabled(False)
        self._double_positive_max_current_filter.setMinimum(0)
        self._double_positive_max_current_filter.setMaximum(9999)
        self._enable_positive_filter.stateChanged.connect(self.onEnablePositiveFilterChanged)
        self._enable_positive_current_filter.stateChanged.connect(self.onEnablePositiveCurrentFilterChanged)
        self._enable_positive_min_current_filter.stateChanged.connect(self.onEnablePositiveMinCurrentFilterChanged)
        self._enable_positive_max_current_filter.stateChanged.connect(self.onEnablePositiveMaxCurrentFilterChanged)
        self._enable_negative_filter.setChecked(True)
        self._enable_negative_current_filter.setChecked(True)
        self._enable_negative_min_current_filter.setDisabled(False)
        self._enable_negative_min_current_filter.setChecked(True)
        self._double_negative_min_current_filter.setDisabled(False)
        self._double_negative_min_current_filter.setMinimum(-9999)
        self._double_negative_min_current_filter.setMaximum(0)
        self._enable_negative_max_current_filter.setDisabled(False)
        self._enable_negative_max_current_filter.setChecked(True)
        self._double_negative_max_current_filter.setDisabled(False)
        self._double_negative_max_current_filter.setMinimum(-9999)
        self._double_negative_max_current_filter.setMaximum(0)
        self._enable_negative_filter.stateChanged.connect(self.onEnableNegativeFilterChanged)
        self._enable_negative_current_filter.stateChanged.connect(self.onEnableNegativeCurrentFilterChanged)
        self._enable_negative_min_current_filter.stateChanged.connect(self.onEnableNegativeMinCurrentFilterChanged)
        self._enable_negative_max_current_filter.stateChanged.connect(self.onEnableNegativeMaxCurrentFilterChanged)
        self._enable_cloud_filter.setChecked(True)
        self.onLayerSelected()
        #self.onEnablePositiveFilterChanged()

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

    def onLayerSelected(self):
        layer = self._layer.currentLayer()
        is_lightning_layer = False
        for field in layer.fields():
            if field.name() == "_correntPic":
                is_lightning_layer = True
        if not is_lightning_layer:
            return
        min_positive = float('inf')
        max_positive = float('-inf')
        min_negative = float('inf')
        max_negative = float('-inf')
        for feat in layer.getFeatures():
            if feat['_nuvolTerra'] == 1:
                if feat['_correntPic'] > 0:
                    if feat['_correntPic'] < min_positive:
                        min_positive = feat['_correntPic']
                    if feat['_correntPic'] > max_positive:
                        max_positive = feat['_correntPic']
                if feat['_correntPic'] < 0:
                    if feat['_correntPic'] < min_negative:
                        min_negative = feat['_correntPic']
                    if feat['_correntPic'] > max_negative:
                        max_negative = feat['_correntPic']
        if min_positive < float('inf'):
            self._double_positive_min_current_filter.setValue(min_positive)
        if max_positive > float('-inf'):
            self._double_positive_max_current_filter.setValue(max_positive)
        if min_negative < float('inf'):
            self._double_negative_min_current_filter.setValue(min_negative)
        if max_negative > float('-inf'):
            self._double_negative_max_current_filter.setValue(max_negative)

    @property
    def positive_filter(self):
        return self._enable_positive_filter.isChecked()

    @positive_filter.setter
    def positive_filter(self, value):
        self._enable_positive_filter.setChecked(value)

    @property
    def positive_current_filter(self):
        return self._enable_positive_current_filter.isChecked()

    @positive_current_filter.setter
    def positive_current_filter(self, value):
        self._enable_positive_current_filter.setChecked(value)

    @property
    def positive_min_current_filter(self):
        return self._enable_positive_min_current_filter.isChecked()

    @positive_min_current_filter.setter
    def positive_min_current_filter(self, value):
        self._enable_positive_min_current_filter.setChecked(value)

    @property
    def positive_max_current_filter(self):
        return self._enable_positive_max_current_filter.isChecked()

    @positive_max_current_filter.setter
    def positive_max_current_filter(self, value):
        self._enable_positive_max_current_filter.setChecked(value)

    @property
    def positive_min_current(self):
        return self._double_positive_min_current_filter.value()

    @positive_min_current.setter
    def positive_min_current(self, value):
        self._double_positive_min_current_filter.setValue(value)

    @property
    def positive_max_current(self):
        return self._double_positive_max_current_filter.value()

    @positive_max_current.setter
    def positive_max_current(self, value):
        self._double_positive_max_current_filter.setValue(value)

    @property
    def negative_filter(self):
        return self._enable_negative_filter.isChecked()

    @negative_filter.setter
    def negative_filter(self, value):
        self._enable_negative_filter.setChecked(value)

    @property
    def negative_current_filter(self):
        return self._enable_negative_current_filter.isChecked()

    @negative_current_filter.setter
    def negative_current_filter(self, value):
        self._enable_negative_current_filter.setChecked(value)

    @property
    def negative_min_current_filter(self):
        return self._enable_negative_min_current_filter.isChecked()

    @negative_min_current_filter.setter
    def negative_min_current_filter(self, value):
        self._enable_negative_min_current_filter.setChecked(value)

    @property
    def negative_max_current_filter(self):
        return self._enable_negative_max_current_filter.isChecked()

    @negative_max_current_filter.setter
    def negative_max_current_filter(self, value):
        self._enable_negative_max_current_filter.setChecked(value)

    @property
    def negative_min_current(self):
        return self._double_negative_min_current_filter.value()

    @negative_min_current.setter
    def negative_min_current(self, value):
        self._double_negative_min_current_filter.setValue(value)

    @property
    def negative_max_current(self):
        return self._double_negative_max_current_filter.value()

    @negative_max_current.setter
    def negative_max_current(self, value):
        self._double_negative_max_current_filter.setValue(value)

    @property
    def cloud_filter(self):
        return self._enable_cloud_filter.isChecked()

    @cloud_filter.setter
    def cloud_filter(self, value):
        self._enable_cloud_filter.setChecked(value)

    @property
    def lightnings_layer(self):
        return self._layer.currentLayer()
