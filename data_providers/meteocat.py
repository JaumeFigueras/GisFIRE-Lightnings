import time
import datetime
import concurrent.futures
import requests
import json
import numpy
from numpy import arange
from math import sin, cos, radians

from qgis.PyQt.QtWidgets import QProgressBar
from qgis.PyQt.QtCore import *
from qgis.core import Qgis
from qgis.gui import QgsMessageBar
from qgis.core import QgsSettings
from qgis.core import QgsProject
from qgis.core import QgsCoordinateReferenceSystem
from qgis.core import QgsCoordinateTransform
from qgis.core import QgsVectorLayer
from qgis.core import QgsField
from qgis.core import QgsGeometry
from qgis.core import QgsApplication
from qgis.core import QgsFeature
from qgis.core import QgsPointXY

from PyQt5.QtCore import QVariant

def download_thread(date, hour, api_key):
    """
    """
    base_url = "https://api.meteo.cat/xdde/v1"
    query = "/catalunya/{0:04d}/{1:02d}/{2:02d}/{3:02d}".format(date.year, date.month, date.day, hour)
    url = base_url + query
    headers = {"x-api-key": "{0:}".format(api_key)}
    r = requests.get(url, headers=headers)
    return (r.status_code == 200, r.json())

def CreateLightningsLayer(type, name):
    """
    """
    # create layer
    vl = QgsVectorLayer(type, name, 'memory')
    pr = vl.dataProvider()
    # add fields
    attributes = [QgsField('id',  QVariant.String),
                    QgsField('data',  QVariant.String),
                    QgsField('correntPic',  QVariant.Double),
                    QgsField('chi2',  QVariant.Double),
                    QgsField('ellipse_eixMajor',  QVariant.Double),
                    QgsField('ellipse_eixMenor',  QVariant.Double),
                    QgsField('ellipse_angle',  QVariant.Double),
                    QgsField('numSensors',  QVariant.Int),
                    QgsField('nuvolTerra',  QVariant.Int),
                    QgsField('idMunicipi',  QVariant.String)]
    pr.addAttributes(attributes)
    vl.updateFields() # tell the vector layer to fetch changes from the provider
    crs = QgsProject.instance().crs()
    vl.setCrs(crs, True)
    # update layer's extent when new features have been added
    # because change of extent in provider is not propagated to the layer
    vl.updateExtents()
    return vl

def AddLayerInPosition(layer, position):
    QgsProject.instance().addMapLayer(layer, True)
    root = QgsProject.instance().layerTreeRoot()
    node_layer = root.findLayer(layer.id())
    node_clone = node_layer.clone()
    parent = node_layer.parent()
    parent.insertChildNode(position, node_clone)
    parent.removeChildNode(node_layer)

def AddLightningPoint(layer, lightning):
    feat = QgsFeature(layer.fields())
    feat.setAttribute('id', str(lightning['id']))
    feat.setAttribute('data', lightning['data'])
    feat.setAttribute('correntPic', float(lightning['correntPic']))
    feat.setAttribute('chi2', float(lightning['chi2']))
    feat.setAttribute('ellipse_eixMajor', float(lightning['ellipse']['eixMajor']))
    feat.setAttribute('ellipse_eixMenor', float(lightning['ellipse']['eixMenor']))
    feat.setAttribute('ellipse_angle', float(lightning['ellipse']['angle']))
    feat.setAttribute('numSensors', int(lightning['numSensors']))
    feat.setAttribute('nuvolTerra', 1 if lightning['nuvolTerra'] else 0)
    if 'idMunicipi' in lightning:
        feat.setAttribute('idMunicipi', lightning['idMunicipi'])
    wgs = QgsCoordinateReferenceSystem(4326)
    tr = QgsCoordinateTransform(wgs, QgsProject.instance().crs(), QgsProject.instance())
    point = QgsGeometry.fromPointXY(QgsPointXY(float(lightning['coordenades']['longitud']), float(lightning['coordenades']['latitud'])))
    point.transform(tr)
    feat.setGeometry(point)
    layer.dataProvider().addFeature(feat)

def AddLightningPolygon(layer, lightning):
    feat = QgsFeature(layer.fields())
    feat.setAttribute('id', str(lightning['id']))
    feat.setAttribute('data', lightning['data'])
    feat.setAttribute('correntPic', float(lightning['correntPic']))
    feat.setAttribute('chi2', float(lightning['chi2']))
    feat.setAttribute('ellipse_eixMajor', float(lightning['ellipse']['eixMajor']))
    feat.setAttribute('ellipse_eixMenor', float(lightning['ellipse']['eixMenor']))
    feat.setAttribute('ellipse_angle', float(lightning['ellipse']['angle']))
    feat.setAttribute('numSensors', int(lightning['numSensors']))
    feat.setAttribute('nuvolTerra', 1 if lightning['nuvolTerra'] else 0)
    if 'idMunicipi' in lightning:
        feat.setAttribute('idMunicipi', lightning['idMunicipi'])
    wgs = QgsCoordinateReferenceSystem(4326)
    tr = QgsCoordinateTransform(wgs, QgsProject.instance().crs(), QgsProject.instance())
    point = QgsGeometry.fromPointXY(QgsPointXY(float(lightning['coordenades']['longitud']), float(lightning['coordenades']['latitud'])))
    point.transform(tr)
    (x, y) = point.asPoint()
    a = float(lightning['ellipse']['eixMajor'])
    b = float(lightning['ellipse']['eixMenor'])
    if b > a:
        b = a
    ds = (2 * numpy.pi) / 100
    ids = arange(0, 2 * numpy.pi, ds)
    points = [(a * cos(ids), b * sin(ids)) for ids in arange(0, 2 * numpy.pi, ds)]
    alpha = radians(float(lightning['ellipse']['angle']) + 90)
    points = [(p[0] * cos(alpha) - p[1] * sin(alpha), p[0] * sin(alpha) + p[1] * cos(alpha)) for p in points]
    points = [(p[0] + x, p[1] + y) for p in points]
    ellipse = [QgsPointXY(p[0], p[1]) for p in points]
    feat.setGeometry(QgsGeometry.fromPolygonXY([ellipse]))
    layer.dataProvider().addFeature(feat)

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
    # Check the lightning layers do not exist
    layer_names = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
    if tr('lighnings') in layer_names or tr('lighning-measurement-error') in layer_names:
        iface.messageBar().pushMessage("", tr("Lightning layers exists, please remove them before downloading new lightnings"), level=Qgis.Critical, duration=5)
        return
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
            while not future.done():
                QgsApplication.instance().processEvents()
            return_value = future.result()
            results.append(return_value)
            if not return_value[0]:
                # Thre has been an error
                iface.messageBar().clearWidgets()
                iface.messageBar().pushMessage("", tr("ERROR downloading Meteo.cat Lightning data. Aborting"), level=Qgis.Critical, duration=5)
                return
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
    # Delete the progress bar
    iface.messageBar().clearWidgets()
