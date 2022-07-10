# -*- coding: utf-8 -*-

from .ui import get_ui_class

from qgis.PyQt.QtWidgets import QDialog
from qgis.core import QgsWkbTypes
from qgis.core import QgsProject
from qgis.core import QgsVectorLayer
from qgis.core import QgsMapLayer
from qgis.core import QgsField
from qgis.core import QgsFeature
from qgis.PyQt.QtWidgets import QDoubleSpinBox
from qgis.PyQt.QtWidgets import QCheckBox
from qgis.PyQt.QtWidgets import QWidget

from typing import List

import os.path

FORM_CLASS = get_ui_class(os.path.dirname(__file__), 'filters.ui')


class DlgFilterLightnings(QDialog, FORM_CLASS):
    """
    Dialog to define the different types of lightnings that will be filtered for the routing process
    """

    cbo_layer: QgsVectorLayer
    spn_double_positive_min_current_filter: QDoubleSpinBox
    spn_double_positive_max_current_filter: QDoubleSpinBox
    spn_double_negative_min_current_filter: QDoubleSpinBox
    spn_double_negative_max_current_filter: QDoubleSpinBox
    chk_enable_positive_filter: QCheckBox
    chk_enable_positive_current_filter: QCheckBox
    chk_enable_positive_min_current_filter: QCheckBox
    chk_enable_positive_max_current_filter: QCheckBox
    chk_enable_negative_filter: QCheckBox
    chk_enable_negative_current_filter: QCheckBox
    chk_enable_negative_min_current_filter: QCheckBox
    chk_enable_negative_max_current_filter: QCheckBox
    chk_enable_cloud_filter: QCheckBox

    def __init__(self, parent: QWidget = None) -> None:
        """
        Constructor.
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        # Create the exclusion list of non-conforming layers
        no_point_layers: List[QgsMapLayer] = list()
        layer: QgsMapLayer
        for layer in QgsProject.instance().mapLayers().values():
            if layer.geometryType() != QgsWkbTypes.PointGeometry:
                no_point_layers.append(layer)
        # Add the list to the widgets to exclude the non-conforming layers
        self.cbo_layer.setExceptedLayerList(no_point_layers)
        # Create the event handlers for the UI responses
        self.cbo_layer.layerChanged.connect(self.__on_layer_selected)
        # Set default values and parameters to the widgets
        self.chk_enable_positive_filter.setChecked(True)
        self.chk_enable_positive_current_filter.setChecked(True)
        self.chk_enable_positive_min_current_filter.setDisabled(False)
        self.chk_enable_positive_min_current_filter.setChecked(True)
        self.spn_double_positive_min_current_filter.setDisabled(False)
        self.spn_double_positive_min_current_filter.setMinimum(0)
        self.spn_double_positive_min_current_filter.setMaximum(9999)
        self.chk_enable_positive_max_current_filter.setDisabled(False)
        self.chk_enable_positive_max_current_filter.setChecked(True)
        self.spn_double_positive_max_current_filter.setDisabled(False)
        self.spn_double_positive_max_current_filter.setMinimum(0)
        self.spn_double_positive_max_current_filter.setMaximum(9999)
        # Create the event handlers for the UI responses
        self.chk_enable_positive_filter.stateChanged.connect(self.__on_enable_positive_filter_changed)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
        self.chk_enable_positive_current_filter.stateChanged.connect(self.__on_enable_positive_current_filter_changed)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
        self.chk_enable_positive_min_current_filter.stateChanged.connect(  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
            self.__on_enable_positive_min_current_filter_changed)
        self.chk_enable_positive_max_current_filter.stateChanged.connect(  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
            self.__on_enable_positive_max_current_filter_changed)
        # Set default values and parameters to the widgets
        self.chk_enable_negative_filter.setChecked(True)
        self.chk_enable_negative_current_filter.setChecked(True)
        self.chk_enable_negative_min_current_filter.setDisabled(False)
        self.chk_enable_negative_min_current_filter.setChecked(True)
        self.spn_double_negative_min_current_filter.setDisabled(False)
        self.spn_double_negative_min_current_filter.setMinimum(-9999)
        self.spn_double_negative_min_current_filter.setMaximum(0)
        self.chk_enable_negative_max_current_filter.setDisabled(False)
        self.chk_enable_negative_max_current_filter.setChecked(True)
        self.spn_double_negative_max_current_filter.setDisabled(False)
        self.spn_double_negative_max_current_filter.setMinimum(-9999)
        self.spn_double_negative_max_current_filter.setMaximum(0)
        # Create the event handlers for the UI responses
        self.chk_enable_negative_filter.stateChanged.connect(self.__on_enable_negative_filter_changed)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
        self.chk_enable_negative_current_filter.stateChanged.connect(self.__on_enable_negative_current_filter_changed)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
        self.chk_enable_negative_min_current_filter.stateChanged.connect(  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
            self.__on_enable_negative_min_current_filter_changed)
        self.chk_enable_negative_max_current_filter.stateChanged.connect(  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
            self.__on_enable_negative_max_current_filter_changed)
        # Set default values and parameters to the widgets
        self.chk_enable_cloud_filter.setChecked(True)
        # Compute the min and max values for a first layer
        self.__on_layer_selected()

    def __on_enable_positive_filter_changed(self) -> None:
        """
        Event handler to respond to the user actions.
        """
        self.chk_enable_positive_current_filter.setDisabled(not self.chk_enable_positive_filter.isChecked())
        if self.chk_enable_positive_filter.isChecked():
            self.chk_enable_positive_min_current_filter.setDisabled(
                not self.chk_enable_positive_current_filter.isChecked())
            self.chk_enable_positive_max_current_filter.setDisabled(
                not self.chk_enable_positive_current_filter.isChecked())
            if self.chk_enable_positive_current_filter.isChecked():
                self.spn_double_positive_min_current_filter.setDisabled(
                    not self.chk_enable_positive_min_current_filter.isChecked())
                self.spn_double_positive_max_current_filter.setDisabled(
                    not self.chk_enable_positive_max_current_filter.isChecked())
            else:
                self.spn_double_positive_min_current_filter.setDisabled(True)
                self.spn_double_positive_max_current_filter.setDisabled(True)
        else:
            self.chk_enable_positive_min_current_filter.setDisabled(True)
            self.chk_enable_positive_max_current_filter.setDisabled(True)
            self.spn_double_positive_min_current_filter.setDisabled(True)
            self.spn_double_positive_max_current_filter.setDisabled(True)

    def __on_enable_positive_current_filter_changed(self) -> None:
        """
        Event handler to respond to the user actions.
        """
        self.chk_enable_positive_min_current_filter.setDisabled(not self.chk_enable_positive_current_filter.isChecked())
        self.chk_enable_positive_max_current_filter.setDisabled(not self.chk_enable_positive_current_filter.isChecked())
        if self.chk_enable_positive_current_filter.isChecked():
            self.spn_double_positive_min_current_filter.setDisabled(
                not self.chk_enable_positive_min_current_filter.isChecked())
            self.spn_double_positive_max_current_filter.setDisabled(
                not self.chk_enable_positive_max_current_filter.isChecked())
        else:
            self.spn_double_positive_min_current_filter.setDisabled(True)
            self.spn_double_positive_max_current_filter.setDisabled(True)

    def __on_enable_positive_min_current_filter_changed(self) -> None:
        """
        Event handler to respond to the user actions.
        """
        self.spn_double_positive_min_current_filter.setDisabled(
            not self.chk_enable_positive_min_current_filter.isChecked())

    def __on_enable_positive_max_current_filter_changed(self) -> None:
        """
        Event handler to respond to the user actions.
        """
        self.spn_double_positive_max_current_filter.setDisabled(
            not self.chk_enable_positive_max_current_filter.isChecked())

    def __on_enable_negative_filter_changed(self) -> None:
        """
        Event handler to respond to the user actions.
        """
        self.chk_enable_negative_current_filter.setDisabled(not self.chk_enable_negative_filter.isChecked())
        if self.chk_enable_negative_filter.isChecked():
            self.chk_enable_negative_min_current_filter.setDisabled(
                not self.chk_enable_negative_current_filter.isChecked())
            self.chk_enable_negative_max_current_filter.setDisabled(
                not self.chk_enable_negative_current_filter.isChecked())
            if self.chk_enable_negative_current_filter.isChecked():
                self.spn_double_negative_min_current_filter.setDisabled(
                    not self.chk_enable_negative_min_current_filter.isChecked())
                self.spn__double_negative_max_current_filter.setDisabled(
                    not self.chk_enable_negative_max_current_filter.isChecked())
            else:
                self.spn_double_negative_min_current_filter.setDisabled(True)
                self.spn_double_negative_max_current_filter.setDisabled(True)
        else:
            self.chk_enable_negative_min_current_filter.setDisabled(True)
            self.chk_enable_negative_max_current_filter.setDisabled(True)
            self.spn_double_negative_min_current_filter.setDisabled(True)
            self.spn_double_negative_max_current_filter.setDisabled(True)

    def __on_enable_negative_current_filter_changed(self) -> None:
        """
        Event handler to respond to the user actions.
        """
        self.chk_enable_negative_min_current_filter.setDisabled(not self.chk_enable_negative_current_filter.isChecked())
        self.chk_enable_negative_max_current_filter.setDisabled(not self.chk_enable_negative_current_filter.isChecked())
        if self.chk_enable_negative_current_filter.isChecked():
            self.spn_double_negative_min_current_filter.setDisabled(
                not self.chk_enable_negative_min_current_filter.isChecked())
            self.spn_double_negative_max_current_filter.setDisabled(
                not self.chk_enable_negative_max_current_filter.isChecked())
        else:
            self.spn_double_negative_min_current_filter.setDisabled(True)
            self.spn_double_negative_max_current_filter.setDisabled(True)

    def __on_enable_negative_min_current_filter_changed(self) -> None:
        """
        Event handler to respond to the user actions.
        """
        self.spn_double_negative_min_current_filter.setDisabled(
            not self.chk_enable_negative_min_current_filter.isChecked())

    def __on_enable_negative_max_current_filter_changed(self) -> None:
        """
        Event handler to respond to the user actions.
        """
        self.spn_double_negative_max_current_filter.setDisabled(
            not self.chk_enable_negative_max_current_filter.isChecked())

    def __on_layer_selected(self) -> None:
        """
        Event handler to respond to the user actions.
        """
        layer: QgsMapLayer = self.cbo_layer.currentLayer()
        if layer is None:
            return
        is_lightning_layer: bool = False
        field: QgsField
        for field in layer.fields():
            if field.name() == "peak_current":
                is_lightning_layer = True
                break
        if not is_lightning_layer:
            return
        min_positive: float = float('inf')
        max_positive: float = float('-inf')
        min_negative: float = float('inf')
        max_negative: float = float('-inf')
        feature: QgsFeature
        for feature in layer.getFeatures():
            if feature['hit_ground'] == 1:
                if feature['peak_current'] > 0:
                    if feature['peak_current'] < min_positive:
                        min_positive = feature['peak_current']
                    if feature['peak_current'] > max_positive:
                        max_positive = feature['peak_current']
                if feature['peak_current'] < 0:
                    if feature['peak_current'] < min_negative:
                        min_negative = feature['peak_current']
                    if feature['peak_current'] > max_negative:
                        max_negative = feature['peak_current']
        if min_positive < float('inf'):
            self.spn_double_positive_min_current_filter.setValue(min_positive)
        if max_positive > float('-inf'):
            self.spn_double_positive_max_current_filter.setValue(max_positive)
        if min_negative < float('inf'):
            self.spn_double_negative_min_current_filter.setValue(min_negative)
        if max_negative > float('-inf'):
            self.spn_double_negative_max_current_filter.setValue(max_negative)

    @property
    def positive_filter(self) -> bool:
        return self.chk_enable_positive_filter.isChecked()

    @positive_filter.setter
    def positive_filter(self, value: bool) -> None:
        self.chk_enable_positive_filter.setChecked(value)

    @property
    def positive_current_filter(self) -> bool:
        return self.chk_enable_positive_current_filter.isChecked()

    @positive_current_filter.setter
    def positive_current_filter(self, value: bool) -> None:
        self.chk_enable_positive_current_filter.setChecked(value)

    @property
    def positive_min_current_filter(self) -> bool:
        return self.chk_enable_positive_min_current_filter.isChecked()

    @positive_min_current_filter.setter
    def positive_min_current_filter(self, value: bool) -> None:
        self.chk_enable_positive_min_current_filter.setChecked(value)

    @property
    def positive_max_current_filter(self) -> bool:
        return self.chk_enable_positive_max_current_filter.isChecked()

    @positive_max_current_filter.setter
    def positive_max_current_filter(self, value: bool) -> None:
        self.chk_enable_positive_max_current_filter.setChecked(value)

    @property
    def positive_min_current(self) -> float:
        return self.spn_double_positive_min_current_filter.value()

    @positive_min_current.setter
    def positive_min_current(self, value: float) -> None:
        self.spn_double_positive_min_current_filter.setValue(value)

    @property
    def positive_max_current(self) -> float:
        return self.spn_double_positive_max_current_filter.value()

    @positive_max_current.setter
    def positive_max_current(self, value: float) -> None:
        self.spn_double_positive_max_current_filter.setValue(value)

    @property
    def negative_filter(self) -> bool:
        return self.chk_enable_negative_filter.isChecked()

    @negative_filter.setter
    def negative_filter(self, value: bool) -> None:
        self.chk_enable_negative_filter.setChecked(value)

    @property
    def negative_current_filter(self) -> bool:
        return self.chk_enable_negative_current_filter.isChecked()

    @negative_current_filter.setter
    def negative_current_filter(self, value: bool) -> None:
        self.chk_enable_negative_current_filter.setChecked(value)

    @property
    def negative_min_current_filter(self) -> bool:
        return self.chk_enable_negative_min_current_filter.isChecked()

    @negative_min_current_filter.setter
    def negative_min_current_filter(self, value: bool) -> None:
        self.chk_enable_negative_min_current_filter.setChecked(value)

    @property
    def negative_max_current_filter(self) -> bool:
        return self.chk_enable_negative_max_current_filter.isChecked()

    @negative_max_current_filter.setter
    def negative_max_current_filter(self, value: bool) -> None:
        self.chk_enable_negative_max_current_filter.setChecked(value)

    @property
    def negative_min_current(self) -> float:
        return self.spn_double_negative_min_current_filter.value()

    @negative_min_current.setter
    def negative_min_current(self, value: float) -> None:
        self.spn_double_negative_min_current_filter.setValue(value)

    @property
    def negative_max_current(self) -> float:
        return self.spn_double_negative_max_current_filter.value()

    @negative_max_current.setter
    def negative_max_current(self, value: float) -> None:
        self.spn_double_negative_max_current_filter.setValue(value)

    @property
    def cloud_filter(self) -> bool:
        return self.chk_enable_cloud_filter.isChecked()

    @cloud_filter.setter
    def cloud_filter(self, value: bool) -> None:
        self.chk_enable_cloud_filter.setChecked(value)

    @property
    def lightnings_layer(self) -> QgsVectorLayer:
        return self.cbo_layer.currentLayer()
