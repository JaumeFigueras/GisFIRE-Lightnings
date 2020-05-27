from .ui import get_ui_class

from qgis.PyQt.QtWidgets import QDialog

import os.path

FORM_CLASS = get_ui_class(os.path.dirname(__file__), 'settings.ui')
class DlgSettings(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

    @property
    def meteocat_api_key(self):
        """I'm the 'x' property."""
        return self.txtMeteoCatApiKey.text()

    @meteocat_api_key.setter
    def meteocat_api_key(self, value):
        self.txtMeteoCatApiKey.setText(value)
