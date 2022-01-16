# -*- coding: utf-8 -*-

from .ui import get_ui_class
from qgis.PyQt.QtWidgets import QDialog
import os.path

FORM_CLASS = get_ui_class(os.path.dirname(__file__), 'settings.ui')


class DlgSettings(QDialog, FORM_CLASS):
    """
    Dialog box to collect or modify the basic settings needed for the GisFIRE Lightnings plugin. The settings are:
    - The Meteocat API Key in case of having to perform a remote request
    - GisFIRE API URL
    - GisFIRE API username
    - GisFIRE API Key

    :type txtMeteoCatApiKey: qgis.PyQt.QtWidgets.QLineEdit
    :type txtGisFireApiBaseUrl: qgis.PyQt.QtWidgets.QLineEdit
    :type txtGisFireApiUsername: qgis.PyQt.QtWidgets.QLineEdit
    :type txtGisFireApiToken: qgis.PyQt.QtWidgets.QLineEdit
    """
    def __init__(self, parent=None):
        """
        TODO
        :param parent:
        :type parent:
        """
        self.txtMeteoCatApiKey = None
        self.txtGisFireApiBaseUrl = None
        self.txtGisFireApiUsername = None
        self.txtGisFireApiToken = None
        QDialog.__init__(self, parent)
        self.setupUi(self)

    @property
    def meteocat_api_key(self):
        """
        TODO

        :return:
        :rtype:
        """
        return self.txtMeteoCatApiKey.text()

    @meteocat_api_key.setter
    def meteocat_api_key(self, value):
        """
        TODO

        :param value:
        :type value:
        """
        self.txtMeteoCatApiKey.setText(value)

    @property
    def gisfire_api_url(self):
        """
        TODO

        :return:
        :rtype:
        """
        return self.txtGisFireApiBaseUrl.text()

    @gisfire_api_url.setter
    def gisfire_api_url(self, value):
        """
        TODO

        :param value:
        :type value:
        """
        self.txtGisFireApiBaseUrl.setText(value)

    @property
    def gisfire_api_username(self):
        """
        TODO

        :return:
        :rtype:
        """
        return self.txtGisFireApiUsername.text()

    @gisfire_api_username.setter
    def gisfire_api_username(self, value):
        """
        TODO

        :param value:
        :type value:
        """
        self.txtGisFireApiUsername.setText(value)

    @property
    def gisfire_api_token(self):
        """
        TODO

        :return:
        :rtype:
        """
        return self.txtGisFireApiToken.text()

    @gisfire_api_token.setter
    def gisfire_api_token(self, value):
        """
        TODO

        :param value:
        :type value:
        """
        self.txtGisFireApiToken.setText(value)
