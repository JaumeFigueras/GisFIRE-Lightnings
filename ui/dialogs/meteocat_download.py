from .ui import get_ui_class

from qgis.PyQt.QtWidgets import QDialog

import os.path
from datetime import datetime
from datetime import timedelta

FORM_CLASS = get_ui_class(os.path.dirname(__file__), 'meteocat_download.ui')
class DlgMeteocatDownload(QDialog, FORM_CLASS):
    """Dialog to set te download dates for the lightnings."""

    def __init__(self, parent=None):
        """Constructor."""
        QDialog.__init__(self, parent)
        self.setupUi(self)
        # Set up iniitial value at yesterday
        yesterday = datetime.utcnow() - timedelta(days=1)
        today = datetime.utcnow()
        self._cal_download_day.setSelectedDate(yesterday)
        self._cal_download_day.setMaximumDate(today)

    @property
    def meteocat_download_day(self):
        return self._cal_download_day.selectedDate().toPyDate()
