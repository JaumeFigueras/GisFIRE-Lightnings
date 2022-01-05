#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os.path

from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtCore import QTranslator
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5.QtWidgets import QMenu

from qgis.utils import active_plugins


class GisFIRELightnings:
    """
    GisFIRE Lightnings QGIS plugin implementation
    """
    def __init__(self, iface):
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
            'GisFIRELightnings_{}.qm'.format(locale))

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
        self._dock_widget = None
        # Initialization of GisFIRE data layers
        self._layers = {}

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """
        Get the translation for a string using Qt translation API.

        :param message: String for translation.
        :type message: str, QString
        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GisFIRELightnings', message)

    def __add_toolbar_actions(self):
        """
        Creates the toolbar buttons that GisFIRE Lightnings uses as shortcuts.
        """
        # Setup parameters
        action = QAction(
            QIcon(':/plugins/gis_fire_lightnings/setup.png'),
            self.tr('Setup GisFIRE Lightnings'),
            None
        )
        action.triggered.connect(self.__on_setup)
        action.setEnabled(True)
        action.setCheckable(False)
        action.setStatusTip(self.tr('Setup GisFIRE Lightnings'))
        action.setWhatsThis(self.tr('Setup GisFIRE Lightnings'))
        self._toolbar.addAction(action)
        self._toolbar_actions['setup'] = action
        # Separator
        self._toolbar.addSeparator()
        # Meteo.cat Download lightnings
        action = QAction(
            QIcon(':/plugins/gis_fire_lightnings/meteocat-lightnings.png'),
            self.tr('Download meteo.cat Lightnings'),
            None
        )
        action.triggered.connect(self.onDownloadMeteoCatLightnings)
        action.setEnabled(True)
        action.setCheckable(False)
        action.setStatusTip(self.tr('Download meteo.cat Lightnings'))
        action.setWhatsThis(self.tr('Download meteo.cat Lightnings'))
        self._toolbar.addAction(action)
        self._toolbar_actions['download-meteocat-lightnings'] = action
        # Clip lightnings
        action = QAction(
            QIcon(':/plugins/gis_fire_lightnings/clip-lightnings.png'),
            self.tr('Clip lightnings on layer and features'),
            None
        )
        action.triggered.connect(self.onClipLightnings)
        action.setEnabled(True)
        action.setCheckable(False)
        action.setStatusTip(self.tr('Clip lightnings on layer and features'))
        action.setWhatsThis(self.tr('Clip lightnings on layer and features'))
        self._toolbar.addAction(action)
        self._toolbar_actions['clip-lightnings'] = action
        # Clip lightnings
        action = QAction(
            QIcon(':/plugins/gis_fire_lightnings/filter-lightnings.png'),
            self.tr('Filter lightnings'),
            None
        )
        action.triggered.connect(self.onFilterLightnings)
        action.setEnabled(True)
        action.setCheckable(False)
        action.setStatusTip(self.tr('Filter lightnings'))
        action.setWhatsThis(self.tr('Filter lightnings'))
        self._toolbar.addAction(action)
        self._toolbar_actions['filter-lightnings'] = action
        # Process lightnings
        action = QAction(
            QIcon(':/plugins/gis_fire_lightnings/process-lightnings.png'),
            self.tr('Calculate lightnings route'),
            None
        )
        action.triggered.connect(self.onProcessLightnings)
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
        action = self._menu.addAction(self.tr('Setup'))
        action.setIcon(QIcon(':/plugins/gis_fire_lightnings/setup.png'))
        action.setIconVisibleInMenu(True)
        action.triggered.connect(self.onSetup)
        self._menu_actions['setup'] = action
        # Meteo.cat Download lightnings
        action = self._menu.addAction(self.tr('Download meteo.cat Lightnings'))
        action.setIcon(QIcon(':/plugins/gis_fire_lightnings/meteocat-lightnings.png'))
        action.setIconVisibleInMenu(True)
        action.triggered.connect(self.onDownloadMeteoCatLightnings)
        self._menu_actions['download-meteocat-lightnings'] = action
        # Clip lightnings
        action = self._menu.addAction(self.tr('Clip lightnings on layer and features'))
        action.setIcon(QIcon(':/plugins/gis_fire_lightnings/clip-lightnings.png'))
        action.setIconVisibleInMenu(True)
        action.triggered.connect(self.onClipLightnings)
        self._menu_actions['clip-lightnings'] = action
        # Filter lightnings
        action = self._menu.addAction(self.tr('Filter lightnings'))
        action.setIcon(QIcon(':/plugins/gis_fire_lightnings/filter-lightnings.png'))
        action.setIconVisibleInMenu(True)
        action.triggered.connect(self.onFilterLightnings)
        self._menu_actions['clip-lightnings'] = action
        # Process lightnings
        action = self._menu.addAction(self.tr('Calculate lightnings route'))
        action.setIcon(QIcon(':/plugins/gis_fire_lightnings/process-lightnings.png'))
        action.setIconVisibleInMenu(True)
        action.triggered.connect(self.onProcessLightnings)
        self._menu_actions['process-lightnings'] = action

    def __add_relations(self):
        """
        Creates mutually exclusive relations between toolbar buttons.
        """
        pass

    # noinspection PyPep8Naming
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
        # Create the menu if does not exist and add it to the current menubar
        if self._menu_gisfire is None:
            self._menu_gisfire = QMenu(menu_name, self.iface.mainWindow().menuBar())
            actions = self.iface.mainWindow().menuBar().actions()
            self.iface.mainWindow().menuBar().insertMenu(actions[-1], self._menu_gisfire)
        # Create Lightnings menu
        self._menu = QMenu(self.tr(u'Lightnings'), self._menu_gisfire)
        self._menu_gisfire.addMenu(self._menu)
        # Set up the toolbar for lightnings plugin
        self._toolbar = self.iface.addToolBar(u'GisFIRE Lightnings')
        self._toolbar.setObjectName(u'GisFIRE Lightnings')
        # Set up the GisFire pane
        self._dock_widget = None

        # Add toolbar buttons
        self.__add_toolbar_actions()
        # Add menu entries
        self.__add_menu_actions()
        # Create relations with existing menus and buttons
        self.__add_relations()

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
        # Remove dock_widget
        if self._dock_widget is not None:
            self._dock_widget.hide()
            self._dock_widget.deleteLater()
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

