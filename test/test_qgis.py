import pytest
import qgis.utils
from pathlib import Path
import sys
from qgis.PyQt.QtWidgets import QDialogButtonBox
import qgis.PyQt.QtTest as QtTest
import qgis.PyQt.QtCore as QtCore
from PyQt5.QtCore import QTimer
from src.gisfire_lightnings.ui.dialogs.settings import DlgSettings


@pytest.mark.parametrize('qgis_app', [{}, {'locale': 'EN'}, {'locale': 'CA'}], indirect=True)
def test_plugin_is_loaded_01(qgis_app):
    _, _, _ = qgis_app
    root_folder = Path(__file__).parent.parent
    qgis.utils.plugin_paths.append(str(root_folder) + '/src')
    if str(root_folder) + '/src' not in sys.path:
        sys.path.insert(0, str(root_folder) + '/src')
    qgis.utils.updateAvailablePlugins()
    assert qgis.utils.loadPlugin('gisfire_lightnings')
    assert qgis.utils.startPlugin('gisfire_lightnings')
    assert type(qgis.utils.plugins['gisfire_lightnings']).__name__ == 'GisFIRELightnings'
    qgis.utils.unloadPlugin('gisfire_lightnings')
    del qgis.utils.plugin_times['gisfire_lightnings']
    sys.path.remove(str(root_folder) + '/src')
    qgis.utils.plugin_paths.remove(str(root_folder) + '/src')
    qgis.utils.updateAvailablePlugins()


@pytest.mark.parametrize('qgis_app', [{'plugin_names': 'gisfire_lightnings'}], indirect=True)
def test_plugin_is_loaded_02(qgis_app):
    _, _, _, plugins = qgis_app
    assert type(plugins[0]).__name__ == 'GisFIRELightnings'


@pytest.mark.parametrize('qgis_app', [{'plugin_names': ['gisfire_lightnings']}], indirect=True)
def test_plugin_is_loaded_03(qgis_app):
    _, _, _, plugins = qgis_app
    assert type(plugins[0]).__name__ == 'GisFIRELightnings'


@pytest.mark.parametrize('qgis_app', [{'plugin_names': 'gisfire_lightnings', 'locale': 'CA'}], indirect=True)
def test_plugin_is_loaded_04(qgis_app):
    _, _, _, plugins = qgis_app
    assert type(plugins[0]).__name__ == 'GisFIRELightnings'


# noinspection DuplicatedCode
@pytest.mark.parametrize('qgis_app', [{'plugin_names': 'gisfire_lightnings'}], indirect=True)
def test_settings_dialog_is_cancelled_01(qgis_app):
    qgs, _, settings, plugins = qgis_app

    def on_timer():
        dlg = plugins[0]._dlg
        QtTest.QTest.mouseClick(dlg.buttonBox.button(QDialogButtonBox.Cancel), QtCore.Qt.LeftButton)

    settings.setValue("gisfire_lightnings/meteocat_api_key", '')
    settings.setValue("gisfire_lightnings/gisfire_api_url", '')
    settings.setValue("gisfire_lightnings/gisfire_api_username", '')
    settings.setValue("gisfire_lightnings/gisfire_api_token", '')
    QTimer.singleShot(500, on_timer)
    plugins[0]._toolbar_actions['setup'].trigger()
    assert settings.value("gisfire_lightnings/meteocat_api_key", "") == ''
    assert settings.value("gisfire_lightnings/gisfire_api_url", "") == ''
    assert settings.value("gisfire_lightnings/gisfire_api_username", "") == ''
    assert settings.value("gisfire_lightnings/gisfire_api_token", "") == ''


# noinspection DuplicatedCode
@pytest.mark.parametrize('qgis_app', [{'plugin_names': 'gisfire_lightnings'}], indirect=True)
def test_settings_dialog_is_ok_01(qgis_app):
    qgs, _, settings, plugins = qgis_app

    def on_timer():
        dlg: DlgSettings = plugins[0]._dlg
        dlg.txtMeteoCatApiKey.setText('test_1')
        dlg.txtGisFireApiBaseUrl.setText('test_2')
        dlg.txtGisFireApiUsername.setText('test_3')
        dlg.txtGisFireApiToken.setText('test_4')
        QtTest.QTest.mouseClick(dlg.buttonBox.button(QDialogButtonBox.Ok), QtCore.Qt.LeftButton)

    settings.setValue("gisfire_lightnings/meteocat_api_key", '')
    settings.setValue("gisfire_lightnings/gisfire_api_url", '')
    settings.setValue("gisfire_lightnings/gisfire_api_username", '')
    settings.setValue("gisfire_lightnings/gisfire_api_token", '')
    QTimer.singleShot(500, on_timer)
    plugins[0]._toolbar_actions['setup'].trigger()
    assert settings.value("gisfire_lightnings/meteocat_api_key", "") == 'test_1'
    assert settings.value("gisfire_lightnings/gisfire_api_url", "") == 'test_2'
    assert settings.value("gisfire_lightnings/gisfire_api_username", "") == 'test_3'
    assert settings.value("gisfire_lightnings/gisfire_api_token", "") == 'test_4'


# noinspection DuplicatedCode
@pytest.mark.parametrize('qgis_app', [{'plugin_names': 'gisfire_lightnings', 'locale': 'EN'},
                                      {'plugin_names': 'gisfire_lightnings', 'locale': 'CA'}], indirect=True)
def test_settings_dialog_is_ok_02(qgis_app):
    qgs, _, settings, plugins = qgis_app

    def on_timer():
        dlg: DlgSettings = plugins[0]._dlg
        dlg.txtGisFireApiUsername.setText('test_33_tset')
        QtTest.QTest.mouseClick(dlg.buttonBox.button(QDialogButtonBox.Ok), QtCore.Qt.LeftButton)

    settings.setValue("gisfire_lightnings/meteocat_api_key", 'test_1')
    settings.setValue("gisfire_lightnings/gisfire_api_url", 'test_2')
    settings.setValue("gisfire_lightnings/gisfire_api_username", 'test_3')
    settings.setValue("gisfire_lightnings/gisfire_api_token", 'test_4')
    QTimer.singleShot(500, on_timer)
    plugins[0]._toolbar_actions['setup'].trigger()
    assert settings.value("gisfire_lightnings/meteocat_api_key", "") == 'test_1'
    assert settings.value("gisfire_lightnings/gisfire_api_url", "") == 'test_2'
    assert settings.value("gisfire_lightnings/gisfire_api_username", "") == 'test_33_tset'
    assert settings.value("gisfire_lightnings/gisfire_api_token", "") == 'test_4'


