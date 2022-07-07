# -*- coding: utf-8 -*-

from .ui import get_ui_class
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtWidgets import QWidget
from qgis.PyQt.QtWidgets import QComboBox
from qgis.PyQt.QtWidgets import QCalendarWidget
import os.path
from datetime import datetime
from datetime import timedelta
from typing import Optional
from typing import Union
from typing import List


FORM_CLASS = get_ui_class(os.path.dirname(__file__), 'download_lightnings.ui')


class DlgDownloadLightnings(QDialog, FORM_CLASS):
    """
    Dialog to set te download date and data provider for the lightnings.

    :type cal_download_day: qgis.PyQt.QtWidgets.QCalendarWidget
    :type cbo_data_providers: qgis.PyQt.QtWidgets.QComboBox
    """

    cal_download_day: QCalendarWidget
    cbo_data_providers: QComboBox

    def __init__(self, parent: Optional[Union[QWidget, None]] = None, data_providers: Optional[Union[List[str], None]] = None):
        """
        Constructor. Sets the date and provider list

        :param parent:
        :type parent:
        :param data_providers:
        :type data_providers:
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        # Set up initial value at yesterday
        yesterday = datetime.utcnow() - timedelta(days=1)
        today = datetime.utcnow()
        self.cal_download_day.setSelectedDate(yesterday)
        self.cal_download_day.setMaximumDate(today)
        # Add data providers to Combo  and select the first
        self.cbo_data_providers.addItems(data_providers)
        self.cbo_data_providers.setCurrentIndex(0)

    @property
    def download_day(self) -> datetime.date:
        """
        Download selected day getter

        :return: The selected date
        :rtype: datetime.date
        """
        return self.cal_download_day.selectedDate().toPyDate()

    @property
    def data_provider(self) -> int:
        return self.cbo_data_providers.currentIndex()

