# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GisFIRELightnings
                                 A QGIS plugin
 GisFIRE module to manage lightning information, clustering and routing for
 wildfire surveillance
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-05-20
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Jaume Figueras
        email                : jaume.figueras@upc.edu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QMessageBox
from qgis.utils import active_plugins
from qgis.core import QgsSettings
from qgis.core import Qgis
from qgis.core import QgsProcessingFeatureSourceDefinition
from qgis.core import QgsProcessingFeedback
from qgis.core import QgsApplication
from qgis.gui import QgsMessageBar
from processing.core.Processing import Processing
import processing
# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the DockWidget
from .gis_fire_lightnings_dockwidget import GisFIRELightningsDockWidget
import os.path

# Import UI dialogs
from .ui.dialogs.settings import DlgSettings
from .ui.dialogs.meteocat_download import DlgMeteocatDownload
from .ui.dialogs.clipping import DlgClipping
from .ui.dialogs.filters import DlgFilterLightnings
from .ui.dialogs.compute_tsp import DlgProcessLightnings
from .ui.renderers.renderers import SetLightningsRenderer
from .ui.renderers.renderers import SetClusterRenderer
from .data_providers.lightnings.gisfire import download_meteocat_lightning_data_from_gisfire_api
from .data_providers.lightnings.helper import AddLayerInPosition
from .algorithms.helper import ComputeDistanceMatrix
from .algorithms.general import NonCrossingPaths
from .algorithms.general import GreedyClustering
from .algorithms.general import GetCentroids
from .algorithms.general import ReArrangeClusters
from .data_providers.paths.helper import CreatePathLayer
from .data_providers.paths.helper import CreateClusteredPointsLayer
from .data_providers.paths.helper import AddClusteredLightningPoint
from .data_providers.paths.helper import CreateCentroidsPointsLayer
from .data_providers.paths.helper import AddCentroidPoint
from .data_providers.paths.helper import AddPathPoint
from .data_providers.paths.helper import AddPathLine

class GisFIRELightnings:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
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
            'GisFIRELightnings_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Initialization of UI references
        self._toolbarActions = dict()
        self._menuActions = dict()
        self._menu = None
        self._menu_gisfire = None
        self._toolbar = None
        self._dockwidget = None
        # Initialization of GisFIRE data layers
        self._layers = {}

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GisFIRELightnings', message)

    def _addToolbarActions(self):
        """Create the toolbar buttons that GisFIRE Lightnings uses as
        shortcuts."""
        # Setup parameters
        action = QAction(QIcon(':/plugins/gis_fire_lightnings/setup.png'), self.tr('Setup GisFIRE Lightnings'), None)
        action.triggered.connect(self.onSetup)
        action.setEnabled(True)
        action.setCheckable(False)
        action.setStatusTip(self.tr('Setup GisFIRE Lightnings'))
        action.setWhatsThis(self.tr('Setup GisFIRE Lightnings'))
        self._toolbar.addAction(action)
        self._toolbarActions['setup'] = action
        # Separator
        self._toolbar.addSeparator()
        # Meteo.cat Download lightnings
        action = QAction(QIcon(':/plugins/gis_fire_lightnings/meteocat-lightnings.png'), self.tr('Download meteo.cat Lightnings'), None)
        action.triggered.connect(self.onDownloadMeteoCatLightnings)
        action.setEnabled(True)
        action.setCheckable(False)
        action.setStatusTip(self.tr('Download meteo.cat Lightnings'))
        action.setWhatsThis(self.tr('Download meteo.cat Lightnings'))
        self._toolbar.addAction(action)
        self._toolbarActions['download-meteocat-lightnings'] = action
        # Clip lightnings
        action = QAction(QIcon(':/plugins/gis_fire_lightnings/clip-lightnings.png'), self.tr('Clip lightnings on layer and features'), None)
        action.triggered.connect(self.onClipLightnings)
        action.setEnabled(True)
        action.setCheckable(False)
        action.setStatusTip(self.tr('Clip lightnings on layer and features'))
        action.setWhatsThis(self.tr('Clip lightnings on layer and features'))
        self._toolbar.addAction(action)
        self._toolbarActions['clip-lightnings'] = action
        # Clip lightnings
        action = QAction(QIcon(':/plugins/gis_fire_lightnings/filter-lightnings.png'), self.tr('Filter lightnings'), None)
        action.triggered.connect(self.onFilterLightnings)
        action.setEnabled(True)
        action.setCheckable(False)
        action.setStatusTip(self.tr('Filter lightnings'))
        action.setWhatsThis(self.tr('Filter lightnings'))
        self._toolbar.addAction(action)
        self._toolbarActions['filter-lightnings'] = action
        # Process lightnings
        action = QAction(QIcon(':/plugins/gis_fire_lightnings/process-lightnings.png'), self.tr('Calculate lightnings route'), None)
        action.triggered.connect(self.onProcessLightnings)
        action.setEnabled(True)
        action.setCheckable(False)
        action.setStatusTip(self.tr('Calculate lightnings route'))
        action.setWhatsThis(self.tr('Calculate lightnings route'))
        self._toolbar.addAction(action)
        self._toolbarActions['process-lightnings'] = action

    def _addMenuActions(self):
        """Create the menu entries that allow GisFIRE procedures."""
        # Setup parameters
        action = self._menu.addAction(self.tr('Setup'))
        action.setIcon(QIcon(':/plugins/gis_fire_lightnings/setup.png'))
        action.setIconVisibleInMenu(True)
        action.triggered.connect(self.onSetup)
        self._menuActions['setup'] = action
        # Meteo.cat Download lightnings
        action = self._menu.addAction(self.tr('Download meteo.cat Lightnings'))
        action.setIcon(QIcon(':/plugins/gis_fire_lightnings/meteocat-lightnings.png'))
        action.setIconVisibleInMenu(True)
        action.triggered.connect(self.onDownloadMeteoCatLightnings)
        self._menuActions['download-meteocat-lightnings'] = action
        # Clip lightnings
        action = self._menu.addAction(self.tr('Clip lightnings on layer and features'))
        action.setIcon(QIcon(':/plugins/gis_fire_lightnings/clip-lightnings.png'))
        action.setIconVisibleInMenu(True)
        action.triggered.connect(self.onClipLightnings)
        self._menuActions['clip-lightnings'] = action
        # Filter lightnings
        action = self._menu.addAction(self.tr('Filter lightnings'))
        action.setIcon(QIcon(':/plugins/gis_fire_lightnings/filter-lightnings.png'))
        action.setIconVisibleInMenu(True)
        action.triggered.connect(self.onFilterLightnings)
        self._menuActions['clip-lightnings'] = action
        # Process lightnings
        action = self._menu.addAction(self.tr('Calculate lightnings route'))
        action.setIcon(QIcon(':/plugins/gis_fire_lightnings/process-lightnings.png'))
        action.setIconVisibleInMenu(True)
        action.triggered.connect(self.onProcessLightnings)
        self._menuActions['process-lightnings'] = action


    def _addRelations(self):
        """Create mutually exclusive relations between toolbar buttons."""
        pass

    def initGui(self):
        """Initializes the QGIS GUI for the GisFIRE Lightning plugin."""
        # Setup the menu
        menu_name = self.tr(u'Gis&FIRE')
        parent_menu = self.iface.mainWindow().menuBar()
        # Search if the menu exists (there are other GisFIRE modules installed)
        for action in parent_menu.actions():
            if action.text() == menu_name:
                self._menu_gisfire = action.menu()
        # Create the menu if does not exists and add it to the current menubar
        if self._menu_gisfire is None:
            self._menu_gisfire = QMenu(menu_name, self.iface.mainWindow().menuBar())
            actions = self.iface.mainWindow().menuBar().actions()
            self.iface.mainWindow().menuBar().insertMenu(actions[-1], self._menu_gisfire)
        # Create Lightnings menu
        self._menu = QMenu(self.tr(u'Lightnings'), self._menu_gisfire)
        self._menu_gisfire.addMenu(self._menu)
        # Setup the toolbar for lightnings plugin
        self._toolbar = self.iface.addToolBar(u'GisFIRE Lightnings')
        self._toolbar.setObjectName(u'GisFIRE Lightnings')
        #setup the GisFire pane
        self._dockwidget = None

        # Add toolbar buttons
        self._addToolbarActions()
        # Add menu entries
        self._addMenuActions()
        # Create relations with existing menus and buttons
        self._addRelations()

    #--------------------------------------------------------------------------

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        # Remove toolbar items
        for action in self._toolbarActions.values():
            action.triggered.disconnect()
            self.iface.removeToolBarIcon(action)
            action.deleteLater()
        # Remove toolbar
        if not(self._toolbar is None):
            self._toolbar.deleteLater()
        # Remove menu items
        for action in self._menuActions.values():
            action.triggered.disconnect()
            self._menu.removeAction(action)
            action.deleteLater()
        # Remove menu
        if not(self._menu is None):
            self._menu.deleteLater()
        # Remove dockwidget
        if self._dockwidget != None:
            self._dockwidget.hide()
            self._dockwidget.deleteLater()
        # Remove the menu_gisfire only if I'm the only GisFIRE module installed
        count = 0
        for name in active_plugins:
            if name.startswith('GisFIRE-'):
                count += 1
        if count == 1:
            if not(self._menu_gisfire is None):
                self.iface.mainWindow().menuBar().removeAction(self._menu_gisfire.menuAction())
                self._menu_gisfire.menuAction().deleteLater()
                self._menu_gisfire.deleteLater()

    #--------------------------------------------------------------------------

    def onSetup(self):
        """Display the settings dialog and retrieves the values
        """
        dlg = DlgSettings(self.iface.mainWindow())
        qgs_settings = QgsSettings()
        # Get values and initialize dialog
        dlg.meteocat_api_key = qgs_settings.value("gis_fire_lightnings/meteocat_api_key", "")
        dlg.gisfire_api_url = qgs_settings.value("gis_fire_lightnings/gisfire_api_url", "")
        dlg.gisfire_api_username = qgs_settings.value("gis_fire_lightnings/gisfire_api_username", "")
        dlg.gisfire_api_token = qgs_settings.value("gis_fire_lightnings/gisfire_api_token", "")
        result = dlg.exec_()
        if result == QDialog.Accepted:
            # Store correct values
            qgs_settings.setValue("gis_fire_lightnings/meteocat_api_key", dlg.meteocat_api_key)
            qgs_settings.setValue("gis_fire_lightnings/gisfire_api_url", dlg.gisfire_api_url)
            qgs_settings.setValue("gis_fire_lightnings/gisfire_api_username", dlg.gisfire_api_username)
            qgs_settings.setValue("gis_fire_lightnings/gisfire_api_token", dlg.gisfire_api_token)
            print(dlg.meteocat_api_key)
            print(dlg.gisfire_api_url)
            print(dlg.gisfire_api_username)
            print(dlg.gisfire_api_token)

    def onDownloadMeteoCatLightnings(self):
        """Display the download data from meteocat and starts the download
        procedure if necessary
        """
        # Get values and initialize dialog
        qgs_settings = QgsSettings()
        meteocat_api_key = qgs_settings.value("gis_fire_lightnings/meteocat_api_key", "")
        gisfire_api_url = qgs_settings.value("gis_fire_lightnings/gisfire_api_url", "")
        gisfire_api_username = qgs_settings.value("gis_fire_lightnings/gisfire_api_username", "")
        gisfire_api_token = qgs_settings.value("gis_fire_lightnings/gisfire_api_token", "")
        # Errors
        if meteocat_api_key == "" or len(meteocat_api_key) < 10:
            self.iface.messageBar().pushMessage("", self.tr("MeteoCat API Key missing"), level=Qgis.Critical, duration=5)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(self.tr("Error"))
            msg.setInformativeText(self.tr("MeteoCat API Key missing"))
            msg.setWindowTitle(self.tr("Error"))
            msg.exec_()
            return
        if gisfire_api_url == "" or len(gisfire_api_url) < 10:
            self.iface.messageBar().pushMessage("", self.tr("GisFIRE API URL missing"), level=Qgis.Critical, duration=5)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(self.tr("Error"))
            msg.setInformativeText(self.tr("GisFIRE API URL missing"))
            msg.setWindowTitle(self.tr("Error"))
            msg.exec_()
            return
        if gisfire_api_username == "" or len(gisfire_api_username) < 1:
            self.iface.messageBar().pushMessage("", self.tr("GisFIRE API Username mssing"), level=Qgis.Critical, duration=5)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(self.tr("Error"))
            msg.setInformativeText(self.tr("GisFIRE API Username mssing"))
            msg.setWindowTitle(self.tr("Error"))
            msg.exec_()
            return
        if gisfire_api_token == "" or len(gisfire_api_token) < 10:
            self.iface.messageBar().pushMessage("", self.tr("GisFIRE API token mssing"), level=Qgis.Critical, duration=5)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(self.tr("Error"))
            msg.setInformativeText(self.tr("GisFIRE API token mssing"))
            msg.setWindowTitle(self.tr("Error"))
            msg.exec_()
            return
        # Show dialog
        dlg = DlgMeteocatDownload(self.iface.mainWindow())
        result = dlg.exec_()
        if result == QDialog.Accepted:
            # Download data
            day = dlg.meteocat_download_day
            success, layers = download_meteocat_lightning_data_from_gisfire_api(self.iface, self.tr, day)
            if success:
                SetLightningsRenderer(layers[0], self.tr)
                layers[0].triggerRepaint()
                self.iface.mapCanvas().refresh()

    def onClipLightnings(self):
        dlg = DlgClipping(self.iface.mainWindow())
        result = dlg.exec_()
        if result == QDialog.Accepted:
            # Now we can clip
            lightnings_layer = dlg.lightnings_layer
            polygons_layer = dlg.polygons_layer
            if lightnings_layer.selectedFeatureCount() == 0:
                input = lightnings_layer
            else:
                input = QgsProcessingFeatureSourceDefinition(lightnings_layer.id(), True)
            if polygons_layer.selectedFeatureCount() == 0:
                overlay = polygons_layer
            else:
                overlay = QgsProcessingFeatureSourceDefinition(polygons_layer.id(), True)
            #
            params = {'INPUT': input, 'OVERLAY': overlay, 'OUTPUT': 'memory:'}
            feedback = QgsProcessingFeedback()
            self.iface.messageBar().pushMessage("", self.tr("Clipping Lightnings."), level=Qgis.Info, duration=0)
            QgsApplication.instance().processEvents()
            result = processing.run('native:clip', params, feedback=feedback, is_child_algorithm=False)
            tmp_layer = result['OUTPUT']
            params = {'INPUT': tmp_layer, 'OUTPUT': 'memory:'}
            feedback = QgsProcessingFeedback()
            result = processing.run('native:multiparttosingleparts', params, feedback=feedback, is_child_algorithm=False)
            new_layer = result['OUTPUT']
            new_layer.setName(lightnings_layer.name() + " - " + polygons_layer.name())
            SetLightningsRenderer(new_layer, self.tr)
            AddLayerInPosition(new_layer, 1)
            self.iface.messageBar().clearWidgets()
            new_layer.triggerRepaint()
            self.iface.mapCanvas().refresh()
            QgsApplication.instance().processEvents()

    def onFilterLightnings(self):
        # Show dialog
        dlg = DlgFilterLightnings(self.iface.mainWindow())
        # Get values and initialize dialog
        qgs_settings = QgsSettings()
        dlg.positive_filter = qgs_settings.value("gis_fire_lightnings/positive_filter", "true") == "true"
        dlg.positive_current_filter = qgs_settings.value("gis_fire_lightnings/positive_current_filter", "true") == "true"
        dlg.positive_min_current_filter = qgs_settings.value("gis_fire_lightnings/positive_min_current_filter", "true") == "true"
        dlg.positive_max_current_filter = qgs_settings.value("gis_fire_lightnings/positive_max_current_filter", "true") == "true"
        dlg.negative_filter = qgs_settings.value("gis_fire_lightnings/negative_filter", "true") == "true"
        dlg.negative_current_filter = qgs_settings.value("gis_fire_lightnings/negative_current_filter", "true") == "true"
        dlg.negative_min_current_filter = qgs_settings.value("gis_fire_lightnings/negative_min_current_filter", "true") == "true"
        dlg.negative_max_current_filter = qgs_settings.value("gis_fire_lightnings/negative_max_current_filter", "true") == "true"
        dlg.cloud_filter = qgs_settings.value("gis_fire_lightnings/cloud_filter", "false") == "true"
        # Run dialog
        result = dlg.exec_()
        if result == QDialog.Accepted:
            # Get dialog data and store them
            qgs_settings.setValue("gis_fire_lightnings/positive_filter", "true" if dlg.positive_filter else "false")
            qgs_settings.setValue("gis_fire_lightnings/positive_current_filter", "true" if dlg.positive_current_filter else "false")
            qgs_settings.setValue("gis_fire_lightnings/positive_min_current_filter", "true" if dlg.positive_min_current_filter else "false")
            qgs_settings.setValue("gis_fire_lightnings/positive_max_current_filter", "true" if dlg.positive_max_current_filter else "false")
            qgs_settings.setValue("gis_fire_lightnings/negative_filter", "true" if dlg.negative_filter else "false")
            qgs_settings.setValue("gis_fire_lightnings/negative_current_filter", "true" if dlg.negative_current_filter else "false")
            qgs_settings.setValue("gis_fire_lightnings/negative_min_current_filter", "true" if dlg.negative_min_current_filter else "false")
            qgs_settings.setValue("gis_fire_lightnings/negative_max_current_filter", "true" if dlg.negative_max_current_filter else "false")
            qgs_settings.setValue("gis_fire_lightnings/cloud_filter", "true" if dlg.cloud_filter else "false")
            query_positive = "FALSE"
            if dlg.positive_filter:
                query_positive = "_nuvolTerra = 1 AND _correntPic > 0"
            query_negative = "FALSE"
            if dlg.negative_filter:
                query_negative = "_nuvolTerra = 1 AND _correntPic < 0"
            query_cloud = "FALSE"
            if dlg.cloud_filter:
                query_cloud = "_nuvolTerra = 0"
            query = "( " + query_positive +  " )" + " OR " + "( " + query_negative + " )" +  " OR " + "( " +  query_cloud + " )"
            layer = dlg.lightnings_layer
            layer.setSubsetString(query)

    def onProcessLightnings(self):
        # Show dialog
        dlg = DlgProcessLightnings(self.iface.mainWindow())
        # Get settings values and initialize dialog
        qgs_settings = QgsSettings()
        dlg.helicopter_maximum_distance = int(qgs_settings.value("gis_fire_lightnings/helicopter_maximum_distance", "300"))
        dlg.enable_lightning_grouping = qgs_settings.value("gis_fire_lightnings/enable_lightning_grouping", "true") == "true"
        dlg.grouping_eps = int(qgs_settings.value("gis_fire_lightnings/grouping_eps", "2000"))
        # Run dialog
        result = dlg.exec_()
        if result == QDialog.Accepted:
            # Get dialog data
            lightnings_layer = dlg.lightnings_layer
            helicopter_layer = dlg.helicopter_layer
            # Just one base must be selected
            if helicopter_layer.selectedFeatureCount() != 1:
                self.iface.messageBar().pushMessage("", self.tr("One helicopter base must be selected"), level=Qgis.Critical, duration=5)
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText(self.tr("Error"))
                msg.setInformativeText(self.tr("One helicopter base must be selected"))
                msg.setWindowTitle(self.tr("Error"))
                msg.exec_()
                return
            # Retrieve settings data for future use
            qgs_settings.setValue("gis_fire_lightnings/helicopter_maximum_distance", str(dlg.helicopter_maximum_distance))
            qgs_settings.setValue("gis_fire_lightnings/enable_lightning_grouping", "true" if dlg.enable_lightning_grouping else "false")
            qgs_settings.setValue("gis_fire_lightnings/grouping_eps", str(dlg.grouping_eps))
            # Get the lightnings data from the layer
            lightnings = [{'_id': feat.attributes()[0],
                            '_data': feat.attributes()[1],
                            '_correntPic': feat.attributes()[2],
                            '_chi2': feat.attributes()[3],
                            '_ellipse_eixMajor': feat.attributes()[4],
                            '_ellipse_eixMenor': feat.attributes()[5],
                            '_ellipse_angle': feat.attributes()[6],
                            '_numSensors': feat.attributes()[7],
                            '_nuvolTerra': feat.attributes()[8],
                            '_idMunicipi': feat.attributes()[9],
                            '_lon': feat.attributes()[10],
                            '_lat': feat.attributes()[11],
                            'point': (feat.geometry().asPoint().x(), feat.geometry().asPoint().y())
                            } for feat in lightnings_layer.getFeatures()]
            # Add a local id to the lightnings
            for i in range(len(lightnings)):
                lightnings[i]['id'] = i
            # If we want to create lightning clusters
            if dlg.grouping_eps:
                clustered_lightnings_layer = CreateClusteredPointsLayer(self.tr('clustered-lightnings'))
                clustered_lightnings, number_of_clusters = GreedyClustering(lightnings)
                clusters = GetCentroids(clustered_lightnings)
                arranged_lightnings = clustered_lightnings
                for _ in range(3):
                    arranged_lightnings, changes = ReArrangeClusters(clusters, arranged_lightnings)
                    if changes == 0:
                        break
                    clusters = GetCentroids(arranged_lightnings)
                for clustered_lightning in arranged_lightnings:
                    AddClusteredLightningPoint(clustered_lightnings_layer, clustered_lightning)
                AddLayerInPosition(clustered_lightnings_layer, 1)
                SetClusterRenderer(clustered_lightnings_layer, 'circle', clusters, self.tr)
                centroids_layer = CreateCentroidsPointsLayer(self.tr('cluster-centroids'))
                for cluster in clusters:
                    print(cluster)
                    AddCentroidPoint(centroids_layer, cluster)
                AddLayerInPosition(centroids_layer, 1)
                SetClusterRenderer(centroids_layer, 'triangle', clusters, self.tr)
            # Get the selected base data from the layer
            base = {'id': helicopter_layer.selectedFeatures()[0].attributes()[0],
                    'point': (helicopter_layer.selectedFeatures()[0].geometry().asPoint().x(), helicopter_layer.selectedFeatures()[0].geometry().asPoint().y())
                    }
            centroid_points = [{'id': cluster['id'],
                                'point': cluster['centroid']
                                } for cluster in clusters]
            centroid_points = [base] + centroid_points + [base]
            points = [(point['point'][0], point['point'][1]) for point in centroid_points]
            distance_matrix = ComputeDistanceMatrix(points)
            path = NonCrossingPaths(distance_matrix, list(range(len(points))))
            points_layer = CreatePathLayer('Point', self.tr('visit-points'))
            path_layer = CreatePathLayer('LineString', self.tr('visit-path'))
            line = list()
            for i in range(len(points)):
                pt = {'id': i, 'x': points[path[i]][0], 'y': points[path[i]][1]}
                AddPathPoint(points_layer, pt)
                line.append(pt)
            AddPathLine(path_layer, line)
            AddLayerInPosition(points_layer, 1)
            AddLayerInPosition(path_layer, 1)
            points_layer.triggerRepaint()
            path_layer.triggerRepaint()
            self.iface.mapCanvas().refresh()
            QgsApplication.instance().processEvents()
