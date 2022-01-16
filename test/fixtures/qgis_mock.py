import pytest
import unittest.mock
import sys
import os
import qgis.utils
from pathlib import Path
from qgis.core import QgsApplication
from qgis.gui import QgisInterface
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QMainWindow
from qgis.PyQt.QtWidgets import QMenuBar
from PyQt5.QtCore import QSize
from qgis.core import QgsSettings
from pytest import FixtureRequest


# noinspection PyUnresolvedReferences
# The pytest request param is optional and generates a warning
@pytest.fixture(scope='function')
def qgis_app(request):
    """
    TODO

    :param request:
    :type request: pytest.FixtureRequest
    :return: The QGIS application objects
    :rtype: (QgsApplication, QgisInterface, QgsSettings, (list of object) or None)
    """
    # Collect parameters
    plugin_names = request.param['plugin_names'] if 'plugin_names' in request.param else None
    plugin_paths = request.param['plugin_paths'] if 'plugin_paths' in request.param \
        else [str(Path(__file__).parent.parent.parent) + '/src']
    locale = request.param['locale'] if 'locale' in request.param else 'EN'
    # Create a QGIS Application
    # noinspection PyTypeChecker
    QgsApplication.setPrefixPath('/usr', True)
    qgs = QgsApplication([], True)
    qgs.initQgis()
    # Mock the QGIS Interface
    iface = unittest.mock.Mock(spec=QgisInterface)
    main_window = QMainWindow()
    iface.mainWindow.return_value = main_window
    canvas = QgsMapCanvas(main_window)
    canvas.resize(QSize(400, 400))
    iface.mapCanvas.return_value = canvas
    # Create the settings
    global_settings = QSettings()
    global_settings.setValue('locale/userLocale', locale)
    qgs_settings = QgsSettings()
    qgs_settings_file = qgs_settings.fileName()
    menu = QMenuBar()
    main_window.setMenuBar(menu)
    qgis.utils.iface = iface
    for plugin_path in plugin_paths:
        sys.path.insert(0, plugin_path)
        qgis.utils.plugin_paths.append(plugin_path)
    qgis.utils.updateAvailablePlugins()
    if plugin_names is not None:
        plugins = list()
        if isinstance(plugin_names, str):
            plugin_names = [plugin_names]
        for plugin_name in plugin_names:
            assert qgis.utils.loadPlugin(plugin_name)
            assert qgis.utils.startPlugin(plugin_name)
            plugins.append(qgis.utils.plugins[plugin_name])
        yield qgs, iface, qgs_settings, plugins
        for plugin_name in plugin_names:
            qgis.utils.unloadPlugin(plugin_name)
            del qgis.utils.plugin_times[plugin_name]
        if plugin_paths is not None:
            for plugin_path in plugin_paths:
                sys.path.remove(plugin_path)
                qgis.utils.plugin_paths.remove(plugin_path)
        qgis.utils.updateAvailablePlugins()
    else:
        yield qgs, iface, qgs_settings, None

    os.remove(qgs_settings_file)
    del qgs
