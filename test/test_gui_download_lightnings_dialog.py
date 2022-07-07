import pytest
import qgis.utils
from pathlib import Path
import sys
from qgis.PyQt.QtWidgets import QDialogButtonBox
import qgis.PyQt.QtTest as QtTest
import qgis.PyQt.QtCore as QtCore
from PyQt5.QtCore import QTimer
from qgis.core import QgsApplication
from qgis.core import QgsSettings
from src.gisfire_lightnings.gisfire_lightnings import GisFIRELightnings
from src.gisfire_lightnings.ui.dialogs.settings import DlgSettings
from PyQt5.QtWidgets import QMenu


@pytest.mark.parametrize('qgis_app', [{'plugin_names': 'gisfire_lightnings', 'locale': 'EN'},
                                      {'plugin_names': 'gisfire_lightnings', 'locale': 'CA'}], indirect=True)
def test_download_lightnings_dialog_01(qgis_app):
    """
    Test the OK button from previous settings form

    :param qgis_app: QGIS application fixture
    :type qgis_app: (QgsApplication, QgisInterface, QgsSettings, list of GisFIRELightnings)
    """
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


