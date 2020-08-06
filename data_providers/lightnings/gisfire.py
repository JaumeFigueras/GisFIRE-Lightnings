#import time
import datetime
import concurrent.futures
import requests
from requests.auth import HTTPBasicAuth

from qgis.PyQt.QtWidgets import QProgressBar
from qgis.PyQt.QtCore import *
from qgis.core import Qgis
from qgis.core import QgsSettings
from qgis.core import QgsProject
from qgis.core import QgsApplication

from .meteocat import CreateLightningsLayer
from .meteocat import AddLightningPoint
from .meteocat import AddLightningPolygon
from .helper import AddLayerInPosition

def download_thread_api(date, hour, api_key, url, username, password):
    """Download function of the meteo.cat dataof the selected date and hour. It
    uses tha API KEY provided bu the user to access the meteo.cat resources

    :param date: the date of the data to download
    :type date: datetime.date

    :param hour: the hour of the data to download
    :type hour: int

    :param api_key: the API KEY provided by meteo.cat to access its resources
    :type api_key: string

    :param username: the GISFIRE API username
    :type password: string

    :param passord: tthe GISFIRE API passord
    :type api_key: string

    :return: the success of the download operation and data received as json
    object extracted from the server response
    :type return: (bool, object)
    """
    base_url = url + "/lightnings/meteocat/v1"
    query = "/{0:04d}/{1:02d}/{2:02d}/{3:02d}".format(date.year, date.month, date.day, hour)
    url = base_url + query
    headers = {"x-api-key": "{0:}".format(api_key)}
    r = requests.get(url, headers=headers, auth=HTTPBasicAuth(username, password))
    return (r.status_code == 200, r.json())

def download_meteocat_lightning_data_from_gisfire_api(iface, tr, day):
    """Downloads and process the lighnings of the selected date, taking into
    account the maximum hours that can be downloaded.

    :param iface: The QGis program interface used
    :type iface: QgsInterface

    :param tr: Translate funcion for QT Linguist
    :type tr: function

    :param day: Day to download
    :type day: date
    """
    # Check the lightning layers do not exist
    layer_names = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
    if tr('lighnings') in layer_names or tr('lighning-measurement-error') in layer_names:
        iface.messageBar().pushMessage("", tr("Lightning layers exists, please remove them before downloading new lightnings"), level=Qgis.Critical, duration=5)
        return (False, None)
    # Create a message.
    #TODO: There is a bug where that not show all the progressbar message that
    # is solved creating a new standard message just before
    iface.messageBar().pushMessage("", tr("Downloading Meteo.cat Lightning data through GisFIRE API."), level=Qgis.Info, duration=1)
    # Create the progress bar widget
    progressMessageBar = iface.messageBar().createMessage(tr("Downloading Meteo.cat Lightning data through GisFIRE API."))
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
    meteocat_api_key = qgs_settings.value("gis_fire_lightnings/meteocat_api_key", "")
    gisfire_api_url = qgs_settings.value("gis_fire_lightnings/gisfire_api_url", "")
    gisfire_api_username = qgs_settings.value("gis_fire_lightnings/gisfire_api_username", "")
    gisfire_api_token = qgs_settings.value("gis_fire_lightnings/gisfire_api_token", "")
    # Lauch the threads to download
    results = list()
    for i in range(hours):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(download_thread_api, day, i, meteocat_api_key, gisfire_api_url, gisfire_api_username, gisfire_api_token)
            while not future.done():
                QgsApplication.instance().processEvents()
            return_value = future.result()
            results.append(return_value)
            if not return_value[0]:
                # Thre has been an error
                iface.messageBar().clearWidgets()
                iface.messageBar().pushMessage("", tr("ERROR downloading Meteo.cat Lightning data through GisFIRE API. Aborting"), level=Qgis.Critical, duration=5)
                return (False, None)
        progress.setValue((i * 100) // hours)
    iface.messageBar().clearWidgets()
    # All data has been downloaded merging all arrays
    lightnings = list()
    for _, lighning_list in results:
        lightnings.extend(lighning_list)
    # Create layers
    lightnings_layer = CreateLightningsLayer('Point', tr('lightnings'))
    errors_layer = CreateLightningsLayer('Polygon', tr('lighning-measurement-error'))
    AddLayerInPosition(lightnings_layer, 1)
    AddLayerInPosition(errors_layer, 2)
    node = QgsProject.instance().layerTreeRoot().findLayer(errors_layer)
    if node:
        node.setItemVisibilityChecked(False)
    # Populate data
    iface.messageBar().pushMessage("", tr("Populating Lightning data."), level=Qgis.Info, duration=1)
    progressMessageBar = iface.messageBar().createMessage(tr("Populating Lightning data."))
    progress = QProgressBar()
    progress.setMaximum(100)
    progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
    progressMessageBar.layout().addWidget(progress)
    iface.messageBar().pushWidget(progressMessageBar, Qgis.Info)
    i = 0
    for lightning in lightnings:
        AddLightningPoint(lightnings_layer, lightning)
        AddLightningPolygon(errors_layer, lightning)
        i += 1
        progress.setValue((i * 100) // len(lightnings))
        QgsApplication.instance().processEvents()
    # Delete the progress bar
    iface.messageBar().clearWidgets()
    return (True, (lightnings_layer, errors_layer))
