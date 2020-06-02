import time
import datetime
import concurrent.futures
import requests
import json

from qgis.PyQt.QtWidgets import QProgressBar
from qgis.PyQt.QtCore import *
from qgis.core import Qgis
from qgis.gui import QgsMessageBar
from qgis.core import QgsSettings

def download_thread(date, hour, api_key):
    """
    """
    base_url = "https://api.meteo.cat/xdde/v1"
    query = "/catalunya/{0:04d}/{1:02d}/{2:02d}/{3:02d}".format(date.year, date.month, date.day, hour)
    url = base_url + query
    headers = {"x-api-key": "{0:}".format(api_key)}
    r = requests.get(url, headers=headers)
    return (r.status_code, r.json)

def download_lightning_data(iface, tr, day):
    """Downloads and process the lighnings of the selected date, taking into
    account the maximum hours that can be downloaded.

    :param iface: The QGis program interface used
    :type iface: QgsInterface

    :param tr: Translate funcion for QT Linguist
    :type tr: function

    :param day: Day to download
    :type day: date
    """
    # Create a message. There is a bug where that blocks the message of the
    # progress bar
    iface.messageBar().pushMessage("", tr("Downloading Meteo.cat Lightning data."), level=Qgis.Info, duration=1)
    # Create the progress bar widget
    progressMessageBar = iface.messageBar().createMessage(tr("Downloading Meteo.cat Lightning data."))
    progress = QProgressBar()
    progress.setMaximum(100)
    progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
    progressMessageBar.layout().addWidget(progress)
    iface.messageBar().pushWidget(progressMessageBar, Qgis.Info)
    # Detect how many hours should we download
    today = datetime.datetime.utcnow().date()
    diff = today - day
    if diff.days > 0:
        hours = 24
    else:
        now = datetime.datetime.utcnow()
        hours = now.hour
    # Get the API key
    qgs_settings = QgsSettings()
    api_key = qgs_settings.value("gis_fire_lightnings/meteocat_api_key", "")
    # Lauch the threads to download
    results = list()
    for i in range(hours):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(download_thread, day, i, api_key)
            return_value = future.result()
            results.append(return_value)
        progress.setValue((i * 100) // hours)
    # Delete the progress bar
    iface.messageBar().clearWidgets()
