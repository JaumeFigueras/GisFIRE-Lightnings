#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import datetime

from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtCore import QTranslator
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtCore import QThread
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtWidgets import QMenu
from qgis.PyQt.QtWidgets import QMessageBox

import qgis.utils
from qgis.core import QgsSettings
from qgis.core import Qgis
from qgis.core import QgsProject
from qgis.core import QgsVectorLayer
from qgis.core import QgsProcessingFeatureSourceDefinition
from qgis.core import QgsProcessingFeedback
from qgis.core import QgsApplication
from processing.core.Processing import Processing
from qgis.gui import QgisInterface
import processing

from meteocat.data_model import Lightning

from typing import List

from .resources import *  # noqa
from .data_providers.gisfire.meteocat import DownloadLightningsUsingMeteocat
from .ui.dialogs.settings import DlgSettings
from .ui.dialogs.download_lightnings import DlgDownloadLightnings
from .ui.dialogs.urban_areas import DlgUrbanAreas
from .ui.dialogs.filters import DlgFilterLightnings
from .ui.dialogs.clipping import DlgClipLightnings
from .ui.dialogs.compute_tsp import DlgProcessLightnings
from .ui.renderers.lightnings import set_lightnings_renderer
from .ui.renderers.lightnings import set_cluster_renderer
from .helpers.layers import add_layer_in_position
from .helpers.meteocat import create_lightnings_layer
from .helpers.meteocat import create_clustered_lightnings_layer
from .helpers.meteocat import create_centroids_points_layer
from .helpers.meteocat import create_path_layer
from .helpers.meteocat import add_lightning_point
from .helpers.meteocat import add_lightning_polygon
from .helpers.meteocat import add_clustered_lightning_point
from .helpers.meteocat import add_centroid_point
from .helpers.meteocat import add_path_point
from .helpers.meteocat import add_path_line
from .helpers.algorithms.main import greedy_clustering
from .helpers.algorithms.main import get_centroids
from .helpers.algorithms.main import re_arrange_clusters
from .helpers.algorithms.main import compute_distance_matrix
from .helpers.algorithms.main import non_crossing_paths


class GisFIRELightnings:
    """
    GisFIRE Lightnings QGIS plugin implementation

    TODO: Add attributes information
    """
    iface: QgisInterface

    def __init__(self, iface: QgisInterface):
        """
        Constructor.

        :param iface: An interface instance that will be passed to this class which provides the hook by which you can
        manipulate the QGIS application at run time.
        :type iface: qgis.gui.QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'gisfire_lightnings_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Initialization of UI references
        self._toolbar_actions = dict()
        self._menu_actions = dict()
        self._menu = None
        self._menu_gisfire = None
        self._toolbar = None
        self._dlg = None
        # Initialization of GisFIRE data layers
        self._layers = {}

    # noinspection PyMethodMayBeStatic
    def tr(self, message: str) -> str:
        """
        Get the translation for a string using Qt translation API.

        :param message: String for translation.
        :type message: str
        :returns: Translated version of message.
        :rtype: str
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GisFIRELightnings', message)

    def __add_toolbar_actions(self):
        """
        Creates the toolbar buttons that GisFIRE Lightnings uses as shortcuts.
        """
        # Setup parameters
        action = QAction(
            QIcon(':/gisfire_lightnings/setup.png'),
            self.tr('Setup GisFIRE Lightnings'),
            None
        )
        action.triggered.connect(self.__on_setup)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
        action.setEnabled(True)
        action.setCheckable(False)
        action.setStatusTip(self.tr('Setup GisFIRE Lightnings'))
        action.setWhatsThis(self.tr('Setup GisFIRE Lightnings'))
        self._toolbar.addAction(action)
        self._toolbar_actions['setup'] = action
        # Separator
        self._toolbar.addSeparator()
        # Download lightnings
        action = QAction(
            QIcon(':/gisfire_lightnings/download-lightnings.png'),
            self.tr('Download Lightnings'),
            None
        )
        action.triggered.connect(self.__on_download_lightnings)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
        action.setEnabled(True)
        action.setCheckable(False)
        action.setStatusTip(self.tr('Download Lightnings'))
        action.setWhatsThis(self.tr('Download Lightnings'))
        self._toolbar.addAction(action)
        self._toolbar_actions['download-lightnings'] = action
        # Filter urban lightnings
        action: QAction = QAction(
            QIcon(':/gisfire_lightnings/urban-lightnings.png'),
            self.tr('Filter Urban Lightnings'),
            None
        )
        action.triggered.connect(self.__on_filter_urban_lightnings)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
        action.setEnabled(True)
        action.setCheckable(False)
        action.setStatusTip(self.tr('Filter Urban Lightnings'))
        action.setWhatsThis(self.tr('Filter Urban Lightnings'))
        self._toolbar.addAction(action)
        self._toolbar_actions['urban-lightnings'] = action
        # Clip lightnings
        action = QAction(
            QIcon(':/gisfire_lightnings/clip-lightnings.png'),
            self.tr('Clip lightnings on layer and features'),
            None
        )
        action.triggered.connect(self.__on_clip_lightnings)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
        action.setEnabled(True)
        action.setCheckable(False)
        action.setStatusTip(self.tr('Clip lightnings on layer and features'))
        action.setWhatsThis(self.tr('Clip lightnings on layer and features'))
        self._toolbar.addAction(action)
        self._toolbar_actions['clip-lightnings'] = action
        # Clip lightnings
        action = QAction(
            QIcon(':/gisfire_lightnings/filter-lightnings.png'),
            self.tr('Filter lightnings'),
            None
        )
        action.triggered.connect(self.__on_filter_lightnings)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
        action.setEnabled(True)
        action.setCheckable(False)
        action.setStatusTip(self.tr('Filter lightnings'))
        action.setWhatsThis(self.tr('Filter lightnings'))
        self._toolbar.addAction(action)
        self._toolbar_actions['filter-lightnings'] = action
        # Process lightnings
        action = QAction(
            QIcon(':/gisfire_lightnings/process-lightnings.png'),
            self.tr('Calculate lightnings route'),
            None
        )
        action.triggered.connect(self.__on_process_lightnings)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
        action.setEnabled(True)
        action.setCheckable(False)
        action.setStatusTip(self.tr('Calculate lightnings route'))
        action.setWhatsThis(self.tr('Calculate lightnings route'))
        self._toolbar.addAction(action)
        self._toolbar_actions['process-lightnings'] = action

    def __add_menu_actions(self):
        """
        Creates the menu entries that allow GisFIRE procedures.
        """
        # Setup parameters
        action: QAction = self._menu.addAction(self.tr('Setup'))
        action.setIcon(QIcon(':/gisfire_lightnings/setup.png'))
        action.setIconVisibleInMenu(True)
        action.triggered.connect(self.__on_setup)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
        self._menu_actions['setup'] = action
        # Download lightnings
        action = self._menu.addAction(self.tr('Download Lightnings'))
        action.setIcon(QIcon(':/gisfire_lightnings/download-lightnings.png'))
        action.setIconVisibleInMenu(True)
        action.triggered.connect(self.__on_download_lightnings)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
        self._menu_actions['download-lightnings'] = action
        # Filter Urban lightnings
        action = self._menu.addAction(self.tr('Filter Urban Lightnings'))
        action.setIcon(QIcon(':/gisfire_lightnings/urban-lightnings.png'))
        action.setIconVisibleInMenu(True)
        action.triggered.connect(self.__on_filter_urban_lightnings)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
        self._menu_actions['download-lightnings'] = action
        # Clip lightnings
        action = self._menu.addAction(self.tr('Clip lightnings on layer and features'))
        action.setIcon(QIcon(':/gisfire_lightnings/clip-lightnings.png'))
        action.setIconVisibleInMenu(True)
        action.triggered.connect(self.__on_clip_lightnings)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
        self._menu_actions['clip-lightnings'] = action
        # Filter lightnings
        action = self._menu.addAction(self.tr('Filter lightnings'))
        action.setIcon(QIcon(':/gisfire_lightnings/filter-lightnings.png'))
        action.setIconVisibleInMenu(True)
        action.triggered.connect(self.__on_filter_lightnings)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
        self._menu_actions['clip-lightnings'] = action
        # Process lightnings
        action = self._menu.addAction(self.tr('Calculate lightnings route'))
        action.setIcon(QIcon(':/gisfire_lightnings/process-lightnings.png'))
        action.setIconVisibleInMenu(True)
        action.triggered.connect(self.__on_process_lightnings)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
        self._menu_actions['process-lightnings'] = action

    def __add_relations(self):
        """
        Creates mutually exclusive relations between toolbar buttons.
        """
        pass

    # noinspection PyPep8Naming
    # noinspection DuplicatedCode
    def initGui(self):
        """
        Initializes the QGIS GUI for the GisFIRE Lightning plugin.
        """
        # Set up the menu
        menu_name = self.tr(u'Gis&FIRE')
        parent_menu = self.iface.mainWindow().menuBar()
        # Search if the menu exists (there are other GisFIRE modules installed)
        for action in parent_menu.actions():
            if action.text() == menu_name:
                self._menu_gisfire = action.menu()
        # Create the menu if it does not exist and add it to the current menubar
        if self._menu_gisfire is None:
            self._menu_gisfire = QMenu(menu_name, parent_menu)
            actions = parent_menu.actions()
            if len(actions) > 0:
                self.iface.mainWindow().menuBar().insertMenu(actions[-1], self._menu_gisfire)
            else:
                self.iface.mainWindow().menuBar().addMenu(self._menu_gisfire)
        # Create Lightnings menu
        self._menu = QMenu(self.tr(u'Lightnings'), self._menu_gisfire)
        self._menu.setIcon(QIcon(':/gisfire_lightnings/lightnings.png'))
        self._menu_gisfire.addMenu(self._menu)
        # Set up the toolbar for lightnings plugin
        self._toolbar = self.iface.addToolBar(u'GisFIRE Lightnings')
        self._toolbar.setObjectName(u'GisFIRE Lightnings')

        # Add toolbar buttons
        self.__add_toolbar_actions()
        # Add menu entries
        self.__add_menu_actions()
        # Create relations with existing menus and buttons
        self.__add_relations()

    # noinspection DuplicatedCode
    def unload(self):
        """
        Removes the plugin menu item and icon from QGIS GUI.
        """
        # Remove toolbar items
        for action in self._toolbar_actions.values():
            action.triggered.disconnect()
            self.iface.removeToolBarIcon(action)
            action.deleteLater()
        # Remove toolbar
        if not(self._toolbar is None):
            self._toolbar.deleteLater()
        # Remove menu items
        for action in self._menu_actions.values():
            action.triggered.disconnect()
            self._menu.removeAction(action)
            action.deleteLater()
        # Remove menu
        if not(self._menu is None):
            self._menu.deleteLater()
        # Remove the menu_gisfire only if I'm the only GisFIRE module installed
        count = 0
        for name in qgis.utils.active_plugins:
            if name.startswith('gisfire'):
                count += 1
        if count == 1:
            if not(self._menu_gisfire is None):
                self.iface.mainWindow().menuBar().removeAction(self._menu_gisfire.menuAction())
                self._menu_gisfire.menuAction().deleteLater()
                self._menu_gisfire.deleteLater()

    def __on_setup(self):
        # TODO: Improve setting enabling and disabling data providers
        self._dlg = DlgSettings(self.iface.mainWindow())
        qgs_settings = QgsSettings()
        # Get values and initialize dialog
        self._dlg.meteocat_api_key = qgs_settings.value("gisfire_lightnings/meteocat_api_key", "")
        self._dlg.gisfire_api_url = qgs_settings.value("gisfire_lightnings/gisfire_api_url", "")
        self._dlg.gisfire_api_username = qgs_settings.value("gisfire_lightnings/gisfire_api_username", "")
        self._dlg.gisfire_api_token = qgs_settings.value("gisfire_lightnings/gisfire_api_token", "")
        result = self._dlg.exec_()
        if result == QDialog.Accepted:
            # Store correct values
            qgs_settings.setValue("gisfire_lightnings/meteocat_api_key", self._dlg.meteocat_api_key)
            qgs_settings.setValue("gisfire_lightnings/gisfire_api_url", self._dlg.gisfire_api_url)
            qgs_settings.setValue("gisfire_lightnings/gisfire_api_username", self._dlg.gisfire_api_username)
            qgs_settings.setValue("gisfire_lightnings/gisfire_api_token", self._dlg.gisfire_api_token)

    def __on_download_lightnings(self) -> None:
        """
        TODO: Explain
        """
        # Get values and initialize dialog
        qgs_settings: QgsSettings = QgsSettings()
        meteocat_api_key = qgs_settings.value("gisfire_lightnings/meteocat_api_key", "")
        gisfire_api_url: str = qgs_settings.value("gisfire_lightnings/gisfire_api_url", "")
        gisfire_api_username: str = qgs_settings.value("gisfire_lightnings/gisfire_api_username", "")
        gisfire_api_token: str = qgs_settings.value("gisfire_lightnings/gisfire_api_token", "")
        # Errors
        if meteocat_api_key == "" or len(meteocat_api_key) < 10:
            self.iface.messageBar().pushMessage("", self.tr("MeteoCat API Key missing"), level=Qgis.Critical,
                                                duration=5)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(self.tr("Error"))
            msg.setInformativeText(self.tr("MeteoCat API Key missing"))
            msg.setWindowTitle(self.tr("Error"))
            msg.exec_()
            return
        if gisfire_api_url == "" or len(gisfire_api_url) < 10:
            self.iface.messageBar().pushMessage("", self.tr("GisFIRE API URL missing"), level=Qgis.Critical, duration=5)
            msg: QMessageBox = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(self.tr("Error"))
            msg.setInformativeText(self.tr("GisFIRE API URL missing"))
            msg.setWindowTitle(self.tr("Error"))
            msg.exec_()
            return
        if gisfire_api_username == "" or len(gisfire_api_username) < 1:
            self.iface.messageBar().pushMessage("", self.tr("GisFIRE API Username missing"), level=Qgis.Critical,
                                                duration=5)
            msg: QMessageBox = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(self.tr("Error"))
            msg.setInformativeText(self.tr("GisFIRE API Username missing"))
            msg.setWindowTitle(self.tr("Error"))
            msg.exec_()
            return
        if gisfire_api_token == "" or len(gisfire_api_token) < 10:
            self.iface.messageBar().pushMessage("", self.tr("GisFIRE API token missing"), level=Qgis.Critical,
                                                duration=5)
            msg: QMessageBox = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(self.tr("Error"))
            msg.setInformativeText(self.tr("GisFIRE API token missing"))
            msg.setWindowTitle(self.tr("Error"))
            msg.exec_()
            return
        # Check that the layers do not exist already and can cause conflicts
        layer_names: List[str] = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
        if self.tr('lightnings') in layer_names or self.tr('lightnings-measurement-error') in layer_names:
            self.iface.messageBar().pushMessage("",
                                                self.tr(
                                                    "Lightning layers exists, please remove them before downloading "
                                                    "new lightnings"),
                                                level=Qgis.Critical, duration=5)
            return
        # Show dialog
        dlg: DlgDownloadLightnings = DlgDownloadLightnings(self.iface.mainWindow(), ['MeteoCat'])
        result = dlg.exec_()
        if result == QDialog.Accepted:
            day: datetime.date = dlg.download_day
            self._thread_download_meteocat = QThread()
            self._worker_download_meteocat = DownloadLightningsUsingMeteocat(day, gisfire_api_url,
                                                                             gisfire_api_username, gisfire_api_token,
                                                                             meteocat_api_key, 25831)
            self._worker_download_meteocat.moveToThread(self._thread_download_meteocat)
            self._thread_download_meteocat.started.connect(self._worker_download_meteocat.run)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
            self._worker_download_meteocat.finished.connect(self._thread_download_meteocat.quit)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
            self._worker_download_meteocat.finished.connect(self._worker_download_meteocat.deleteLater)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
            self._thread_download_meteocat.finished.connect(self._thread_download_meteocat.deleteLater)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
            self._worker_download_meteocat.progress.connect(self.__report_progress_download_lightnings_meteocat)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
            self._worker_download_meteocat.data.connect(self.__received_data_download_lightnings_meteocat)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
            self._worker_download_meteocat.finished.connect(self.__report_end_download_lightnings_meteocat)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
            self.iface.messageBar().pushMessage("",
                                                self.tr("Downloading Meteo.cat Lightning data through GisFIRE API."),
                                                level=Qgis.Info, duration=1)
            self._thread_download_meteocat.start()

    def __report_progress_download_lightnings_meteocat(self, n: int) -> None:
        """
        TODO: Explain
        """
        pass

    def __report_end_download_lightnings_meteocat(self) -> None:
        """
        TODO: EXplain
        """
        self.iface.messageBar().pushMessage("", self.tr("Finished."), level=Qgis.Info, duration=1)

    def __received_data_download_lightnings_meteocat(self, lightnings: List[Lightning]) -> None:
        self.iface.messageBar().pushMessage("", self.tr("Received {0:d} lightnings.".format(len(lightnings))),
                                            level=Qgis.Info, duration=1)
        self.lightnings_layer = create_lightnings_layer('Point', 'lightnings', 25831)
        self.lightning_errors_layer = create_lightnings_layer('Polygon', 'lightning-errors', 25831)
        add_layer_in_position(self.lightnings_layer, 1)
        add_layer_in_position(self.lightning_errors_layer, 2)
        for lightning in lightnings:
            add_lightning_point(self.lightnings_layer, lightning)
            add_lightning_polygon(self.lightning_errors_layer, lightning)
        set_lightnings_renderer(self.lightnings_layer, self.tr)
        self.lightnings_layer.updateExtents()
        extent = self.lightnings_layer.extent()
        self.iface.mapCanvas().setExtent(extent)
        self.iface.mapCanvas().refresh()

    def __on_filter_urban_lightnings(self) -> None:
        """
        TODO: Explain
        """
        dlg: DlgUrbanAreas = DlgUrbanAreas(self.iface.mainWindow())
        result = dlg.exec_()
        if result == QDialog.Accepted:
            pass

    def __on_clip_lightnings(self) -> None:
        """
        TODO: Explain
        """
        # Show dialog
        dlg: DlgClipLightnings = DlgClipLightnings(self.iface.mainWindow())
        result: int = dlg.exec_()
        if result == QDialog.Accepted:
            # Now we can clip
            lightnings_layer: QgsVectorLayer = dlg.lightnings_layer
            polygons_layer: QgsVectorLayer = dlg.polygons_layer
            # Select te whole layer or the selected features only to clip
            if lightnings_layer.selectedFeatureCount() == 0:
                input_layer = lightnings_layer
            else:
                input_layer = QgsProcessingFeatureSourceDefinition(lightnings_layer.id(), True)
            if polygons_layer.selectedFeatureCount() == 0:
                overlay_layer = polygons_layer
            else:
                overlay_layer = QgsProcessingFeatureSourceDefinition(polygons_layer.id(), True)
            # Create the processing workflow to clip
            params = {'INPUT': input_layer, 'OVERLAY': overlay_layer, 'OUTPUT': 'memory:'}
            feedback = QgsProcessingFeedback()
            self.iface.messageBar().pushMessage("", self.tr("Clipping Lightnings."), level=Qgis.Info, duration=0)
            QgsApplication.instance().processEvents()
            result = processing.run('native:clip', params, feedback=feedback, is_child_algorithm=False)
            tmp_layer = result['OUTPUT']
            # Results appear as multipart so a single part process is executed
            params = {'INPUT': tmp_layer, 'OUTPUT': 'memory:'}
            feedback = QgsProcessingFeedback()
            result = processing.run('native:multiparttosingleparts', params, feedback=feedback, is_child_algorithm=False)
            new_layer = result['OUTPUT']
            # Add the new layer to the project
            new_layer.setName(lightnings_layer.name() + "-" + polygons_layer.name())
            set_lightnings_renderer(new_layer, self.tr)
            add_layer_in_position(new_layer, 1)
            self.iface.messageBar().clearWidgets()
            new_layer.triggerRepaint()
            self.iface.mapCanvas().refresh()
            QgsApplication.instance().processEvents()

    def __on_filter_lightnings(self) -> None:
        """
        TODO: Explain
        """
        # Show dialog
        dlg:  DlgFilterLightnings = DlgFilterLightnings(self.iface.mainWindow())
        # Get the preferred values and initialize dialog
        qgs_settings: QgsSettings = QgsSettings()
        dlg.positive_filter = qgs_settings.value("gisfire_lightnings/positive_filter", "true") == "true"
        dlg.positive_current_filter = qgs_settings.value("gisfire_lightnings/positive_current_filter", "true") == "true"
        dlg.positive_min_current_filter = qgs_settings.value("gisfire_lightnings/positive_min_current_filter", "true") == "true"
        dlg.positive_max_current_filter = qgs_settings.value("gisfire_lightnings/positive_max_current_filter", "true") == "true"
        dlg.negative_filter = qgs_settings.value("gisfire_lightnings/negative_filter", "true") == "true"
        dlg.negative_current_filter = qgs_settings.value("gisfire_lightnings/negative_current_filter", "true") == "true"
        dlg.negative_min_current_filter = qgs_settings.value("gisfire_lightnings/negative_min_current_filter", "true") == "true"
        dlg.negative_max_current_filter = qgs_settings.value("gisfire_lightnings/negative_max_current_filter", "true") == "true"
        dlg.cloud_filter = qgs_settings.value("gisfire_lightnings/cloud_filter", "false") == "true"
        # Run dialog
        result = dlg.exec_()
        if result == QDialog.Accepted:
            # Get dialog data and store them to the preferences
            qgs_settings.setValue("gisfire_lightnings/positive_filter", "true" if dlg.positive_filter else "false")
            qgs_settings.setValue("gisfire_lightnings/positive_current_filter",
                                  "true" if dlg.positive_current_filter else "false")
            qgs_settings.setValue("gisfire_lightnings/positive_min_current_filter",
                                  "true" if dlg.positive_min_current_filter else "false")
            qgs_settings.setValue("gisfire_lightnings/positive_max_current_filter",
                                  "true" if dlg.positive_max_current_filter else "false")
            qgs_settings.setValue("gisfire_lightnings/negative_filter", "true" if dlg.negative_filter else "false")
            qgs_settings.setValue("gisfire_lightnings/negative_current_filter",
                                  "true" if dlg.negative_current_filter else "false")
            qgs_settings.setValue("gisfire_lightnings/negative_min_current_filter",
                                  "true" if dlg.negative_min_current_filter else "false")
            qgs_settings.setValue("gisfire_lightnings/negative_max_current_filter",
                                  "true" if dlg.negative_max_current_filter else "false")
            qgs_settings.setValue("gisfire_lightnings/cloud_filter", "true" if dlg.cloud_filter else "false")
            # Build the positive query depending on the selected filters
            query_positive: str = "FALSE"
            if dlg.positive_filter:
                query_positive = "hit_ground = 1 AND peak_current > 0"
                if dlg.positive_current_filter and dlg.positive_min_current_filter:
                    query_positive += " AND peak_current >= " + str(dlg.positive_min_current)
                if dlg.positive_current_filter and dlg.positive_max_current_filter:
                    query_positive += " AND peak_current <= " + str(dlg.positive_max_current)
            # Build the negative query depending on the selected filters
            query_negative: str = "FALSE"
            if dlg.negative_filter:
                query_negative = "hit_ground = 1 AND peak_current < 0"
                if dlg.negative_current_filter and dlg.negative_min_current_filter:
                    query_negative += " AND peak_current >= " + str(dlg.negative_min_current)
                if dlg.negative_current_filter and dlg.negative_max_current_filter:
                    query_negative += " AND peak_current <= " + str(dlg.negative_max_current)
            # Build the cloud to cloud query if it is selected
            query_cloud: str = "FALSE"
            if dlg.cloud_filter:
                query_cloud = "hit_ground = 0"
            # Build and apply the combined query
            query: str = "({0:}) OR ({1:}) OR ({2:})".format(query_positive, query_negative, query_cloud)
            layer = dlg.lightnings_layer
            layer.setSubsetString(query)

    def __on_process_lightnings(self) -> None:
        """
        TODO: Explain better
        Display the Process dialog, get the parameters needed and compute the TSP problem ith the selected layers
        """
        # Show dialog
        dlg: DlgProcessLightnings = DlgProcessLightnings(self.iface.mainWindow())
        # Get settings values and initialize dialog
        qgs_settings: QgsSettings = QgsSettings()
        dlg.helicopter_maximum_distance = int(qgs_settings.value("gisfire_lightnings/helicopter_maximum_distance",
                                                                 "300"))
        dlg.enable_lightning_grouping = qgs_settings.value("gisfire_lightnings/enable_lightning_grouping",
                                                           "true") == "true"
        dlg.grouping_eps = int(qgs_settings.value("gisfire_lightnings/grouping_eps", "2000"))
        # Run dialog
        result: int = dlg.exec_()
        if result == QDialog.Accepted:
            # Get dialog data
            lightnings_layer: QgsVectorLayer = dlg.lightnings_layer
            helicopter_layer: QgsVectorLayer = dlg.helicopter_layer
            # Just one base must be selected
            if helicopter_layer.selectedFeatureCount() != 1:
                self.iface.messageBar().pushMessage("", self.tr("One helicopter base must be selected"),
                                                    level=Qgis.Critical, duration=5)
                msg: QMessageBox = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText(self.tr("Error"))
                msg.setInformativeText(self.tr("One helicopter base must be selected"))
                msg.setWindowTitle(self.tr("Error"))
                msg.exec_()
                return
            # Retrieve settings data for future use
            qgs_settings.setValue("gisfire_lightnings/helicopter_maximum_distance", str(dlg.helicopter_maximum_distance))
            qgs_settings.setValue("gisfire_lightnings/enable_lightning_grouping",
                                  "true" if dlg.enable_lightning_grouping else "false")
            qgs_settings.setValue("gisfire_lightnings/grouping_eps", str(dlg.grouping_eps))
            # Get the lightnings or selected lightnings data from the layer
            if len(lightnings_layer.selectedFeatures()) > 0:
                lightnings_iterator = lightnings_layer.selectedFeatures()
            else:
                lightnings_iterator = lightnings_layer.getFeatures()
            # TODO: Add main gisfire id
            lightnings: List[Lightning] = [Lightning(meteocat_id=feature['meteocat_id'],
                                                     date=feature['date'],
                                                     peak_current=feature['peak_current'],
                                                     chi_squared=feature['chi_squared'],
                                                     ellipse_major_axis=feature['ellipse_major_axis'],
                                                     ellipse_minor_axis=feature['ellipse_minor_axis'],
                                                     ellipse_angle=feature['ellipse_angle'],
                                                     number_of_sensors=feature['number_of_sensors'],
                                                     hit_ground=feature['hit_ground'],
                                                     coordinates_longitude=feature.geometry().asPoint().x(),
                                                     coordinates_latitude=feature.geometry().asPoint().y())
                                           for feature in lightnings_iterator]

            # If we want to create lightning clusters
            if dlg.enable_lightning_grouping:
                # Create the cluster layer and clusters
                # TODO: Hardcoded EPSG improve
                clustered_lightnings_layer: QgsVectorLayer = create_clustered_lightnings_layer('Point',self.tr('clustered-lightnings'), 25831)
                clustered_lightnings, number_of_clusters = greedy_clustering(lightnings, eps=dlg.grouping_eps)
                clusters = get_centroids(clustered_lightnings)
                arranged_lightnings = clustered_lightnings
                # Re-arrange clusters depending on centroids
                for _ in range(3):
                    arranged_lightnings, changes = re_arrange_clusters(clusters, arranged_lightnings)
                    if changes == 0:
                        break
                    clusters = get_centroids(arranged_lightnings)
                # Add clusters and centroids into its layers
                for clustered_lightning in arranged_lightnings:
                    add_clustered_lightning_point(clustered_lightnings_layer, clustered_lightning)
                add_layer_in_position(clustered_lightnings_layer, 1)
                set_cluster_renderer(clustered_lightnings_layer, 'circle', clusters)
                centroids_layer = create_centroids_points_layer('Point', self.tr('cluster-centroids'), 25831)
                for cluster in clusters:
                    add_centroid_point(centroids_layer, cluster)
                add_layer_in_position(centroids_layer, 1)
                set_cluster_renderer(centroids_layer, 'triangle', clusters)
            else:
                clusters = [{'id': i, 'centroid':lightnings[i]['point']} for i in range(len(lightnings))]
            # Get the selected helicopter base data from the layer
            base = {'id': helicopter_layer.selectedFeatures()[0].attributes()[0],
                    'point': (helicopter_layer.selectedFeatures()[0].geometry().asPoint().x(), helicopter_layer.selectedFeatures()[0].geometry().asPoint().y())
                    }
            # build the centroid list
            centroid_points = [{'id': cluster['id'],
                                'point': cluster['centroid']
                                } for cluster in clusters]
            centroid_points = [base] + centroid_points + [base]
            # Get the point coordinates and calculate the distance matrix
            points = [(point['point'][0], point['point'][1]) for point in centroid_points]
            distance_matrix = compute_distance_matrix(points)
            # Approximate a TSP searching for a planar path
            path = non_crossing_paths(distance_matrix, list(range(len(points))))
            # Create the results layer
            points_layer = create_path_layer('Point', self.tr('visit-points'), 25831)
            path_layer = create_path_layer('LineString', self.tr('visit-path'), 25831)
            # Add data to layers and show them
            line = list()
            for i in range(len(points)):
                pt = {'id': i, 'x': points[path[i]][0], 'y': points[path[i]][1]}
                add_path_point(points_layer, pt)
                line.append(pt)
            add_path_line(path_layer, line)
            add_layer_in_position(points_layer, 1)
            add_layer_in_position(path_layer, 1)
            length = 0
            for feature in path_layer.getFeatures():
                length = feature.geometry().length()
            if (length / 1000) > dlg.helicopter_maximum_distance:
                self.iface.messageBar().pushMessage("", self.tr("Calculated length of {} km is greater than selected maximum of {} km").format(length//1000, dlg.helicopter_maximum_distance), level=Qgis.Critical, duration=0)
            else:
                self.iface.messageBar().pushMessage("", self.tr("Process correctly finished. Route Length: {} km").format(length//1000), level=Qgis.Info, duration=0)
            points_layer.triggerRepaint()
            path_layer.triggerRepaint()
            self.iface.mapCanvas().refresh()
            QgsApplication.instance().processEvents()
