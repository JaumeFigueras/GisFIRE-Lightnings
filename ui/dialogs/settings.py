from .ui import get_ui_class

from qgis.PyQt.QtWidgets import QDialog

import os.path

FORM_CLASS = get_ui_class(os.path.dirname(__file__), 'settings.ui')
class DlgSettings(QDialog, FORM_CLASS):
    """Dialog to define the different system paraeters."""
    def __init__(self, parent=None):
        """Constructor."""
        QDialog.__init__(self, parent)
        self.setupUi(self)

    @property
    def meteocat_api_key(self):
        return self.txtMeteoCatApiKey.text()

    @meteocat_api_key.setter
    def meteocat_api_key(self, value):
        self.txtMeteoCatApiKey.setText(value)

    @property
    def gisfire_api_url(self):
        return self.txtGisFireApiBaseUrl.text()

    @gisfire_api_url.setter
    def gisfire_api_url(self, value):
        self.txtGisFireApiBaseUrl.setText(value)

    @property
    def gisfire_api_username(self):
        return self.txtGisFireApiUsername.text()

    @gisfire_api_username.setter
    def gisfire_api_username(self, value):
        self.txtGisFireApiUsername.setText(value)

    @property
    def gisfire_api_token(self):
        return self.txtGisFireApiToken.text()

    @gisfire_api_token.setter
    def gisfire_api_token(self, value):
        self.txtGisFireApiToken.setText(value)
