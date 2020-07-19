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
from qgis.core import QgsRuleBasedRenderer
from qgis.core import QgsSymbol
from qgis.core import QgsMarkerSymbol
from qgis.core import QgsUnitTypes

from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor

from .helper import AddLayerInPosition

def download_thread(date, hour, api_key):
    """Download function of the meteo.cat dataof the selected date and hour. It
    uses tha API KEY provided bu the user to access the meteo.cat resources

    :param date: the date of the data to download
    :type date: datetime.date

    :param hour: the hour of the data to download
    :type hour: int

    :param api_key: the API KEY provided by meteo.cat to access its resources
    :type api_key: string

    :return: the success of the download operation and data received as json
    object extracted from the server response
    :type return: (bool, object)
    """
    base_url = "https://api.meteo.cat/xdde/v1"
    query = "/catalunya/{0:04d}/{1:02d}/{2:02d}/{3:02d}".format(date.year, date.month, date.day, hour)
    url = base_url + query
    headers = {"x-api-key": "{0:}".format(api_key)}
    r = requests.get(url, headers=headers)
    return (r.status_code == 200, r.json())

def SetRenderer(layer, tr):
    # Create a default rule renderer to build a new one
    symbol = QgsSymbol.defaultSymbol(layer.geometryType())
    renderer = QgsRuleBasedRenderer(symbol)
    root = renderer.rootRule()
    # Create positive Rule
    rule_positive = root.children()[0].clone()
    rule_positive.setLabel(tr('Positive'))
    rule_positive.setFilterExpression('"correntPic" >= 0 AND "nuvolTerra" = 1')
    symbol = QgsMarkerSymbol.createSimple({'name': 'cross'})
    symbol.setSize(4.0)
    symbol.setSizeUnit(QgsUnitTypes.RenderMillimeters)
    symbol.setColor(QColor('#ff0000'))
    symbol.symbolLayer(0).setStrokeWidth(1.0)
    rule_positive.setSymbol(symbol)
    root.appendChild(rule_positive)
    # Create negative Rule
    rule_negative = root.children()[0].clone()
    rule_negative.setLabel(tr('Negative'))
    rule_negative.setFilterExpression('"correntPic" < 0 AND "nuvolTerra" = 1')
    symbol = QgsMarkerSymbol.createSimple({'name': 'line'})
    symbol.setAngle(90.0)
    symbol.setSize(4.0)
    symbol.setSizeUnit(QgsUnitTypes.RenderMillimeters)
    symbol.setColor(QColor('#00ff00'))
    symbol.symbolLayer(0).setStrokeWidth(1.0)
    rule_negative.setSymbol(symbol)
    root.appendChild(rule_negative)
    # Create positive Rule
    rule_cloudcloud = root.children()[0].clone()
    rule_cloudcloud.setLabel(tr('Cloud - Cloud'))
    rule_cloudcloud.setFilterExpression('"nuvolTerra" = 0')
    symbol = QgsMarkerSymbol.createSimple({'name': 'circle'})
    symbol.setSize(1.0)
    symbol.setSizeUnit(QgsUnitTypes.RenderMillimeters)
    symbol.setColor(QColor('#0000ff'))
    rule_cloudcloud.setSymbol(symbol)
    rule_cloudcloud.setActive(False)
    root.appendChild(rule_cloudcloud)
    # Remove default
    root.removeChildAt(0)
    # set Renderer
    layer.setRenderer(renderer)

def CreateLightningsLayer(type, name):
    """Create a QGis vector layer with the attributes specified by the meteo.cat
    API definition

    :param type: defines the feature type of the layer, meteo.cat provides
    information to construct a point layer or a polygon layer
    :type type: string with two possible values 'Point' or 'Polygon'

    :param name: name of the layer that will be shown in the QGis legend
    :type name: string

    :return: the function returns the newly created layer or None depending on
    the correct feature type provided
    :type return: qgis.core.QgsVectorLayer or None
    """
    # Check allowed feature types
    if type != 'Point' and type != 'Polygon':
        return None
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
                    QgsField('idMunicipi',  QVariant.String),
                    QgsField('lon',  QVariant.Double),
                    QgsField('lat',  QVariant.Double)]
    pr.addAttributes(attributes)
    vl.updateFields() # tell the vector layer to fetch changes from the provider
    # Assign current project CRS
    crs = QgsProject.instance().crs()
    vl.setCrs(crs, True)
    # Update layer's extent because change of extent in provider is not
    # propagated to the layer
    vl.updateExtents()
    return vl

def AddLightningPoint(layer, lightning):
    """Add a lightning location with its information to the point layer provided

    :param layer: data layer where the lightning will be added
    :type type: qgis.core.QgsVectorLayer

    :param name: data object provided by meteo.cat with lightning information
    :type name: object
    """
    # create the feature
    feat = QgsFeature(layer.fields())
    # add attributes
    feat.setAttribute('id', str(lightning['id']))
    feat.setAttribute('data', lightning['data'])
    feat.setAttribute('correntPic', float(lightning['correntPic']))
    feat.setAttribute('chi2', float(lightning['chi2']))
    feat.setAttribute('ellipse_eixMajor', float(lightning['ellipse']['eixMajor']))
    feat.setAttribute('ellipse_eixMenor', float(lightning['ellipse']['eixMenor']))
    feat.setAttribute('ellipse_angle', float(lightning['ellipse']['angle']))
    feat.setAttribute('numSensors', int(lightning['numSensors']))
    feat.setAttribute('nuvolTerra', 1 if lightning['nuvolTerra'] else 0)
    feat.setAttribute('lon', float(lightning['coordenades']['longitud']))
    feat.setAttribute('lat', float(lightning['coordenades']['latitud']))
    # municipality id its not always present, depends if the lightning location
    # is inside Catalonia land or outside (Aragon, Valencia, France or the sea)
    if 'idMunicipi' in lightning:
        feat.setAttribute('idMunicipi', lightning['idMunicipi'])
    #TODO: We do not really wnow it data is in EPSG:4326 (WGS84) or
    # EPSG:4258 (ETRS89)
    etrs_geo = QgsCoordinateReferenceSystem(4258)
    tr = QgsCoordinateTransform(etrs_geo, QgsProject.instance().crs(), QgsProject.instance())
    point = QgsGeometry.fromPointXY(QgsPointXY(float(lightning['coordenades']['longitud']), float(lightning['coordenades']['latitud'])))
    point.transform(tr)
    feat.setGeometry(point)
    layer.dataProvider().addFeature(feat)

def AddLightningPolygon(layer, lightning):
    """Add a lightning error ellipse location with its information to the
    polygon layer provided

    :param layer: data layer where the lightning error ellipse will be added
    :type type: qgis.core.QgsVectorLayer

    :param name: data object provided by meteo.cat with lightning information
    :type name: object
    """
    # create the feature
    feat = QgsFeature(layer.fields())
    # add attributes
    feat.setAttribute('id', str(lightning['id']))
    feat.setAttribute('data', lightning['data'])
    feat.setAttribute('correntPic', float(lightning['correntPic']))
    feat.setAttribute('chi2', float(lightning['chi2']))
    feat.setAttribute('ellipse_eixMajor', float(lightning['ellipse']['eixMajor']))
    feat.setAttribute('ellipse_eixMenor', float(lightning['ellipse']['eixMenor']))
    feat.setAttribute('ellipse_angle', float(lightning['ellipse']['angle']))
    feat.setAttribute('numSensors', int(lightning['numSensors']))
    feat.setAttribute('nuvolTerra', 1 if lightning['nuvolTerra'] else 0)
    feat.setAttribute('lon', float(lightning['coordenades']['longitud']))
    feat.setAttribute('lat', float(lightning['coordenades']['latitud']))
    # municipality id its not always present, depends if the lightning location
    # is inside Catalonia land or outside (Aragon, Valencia, France or the sea)
    if 'idMunicipi' in lightning:
        feat.setAttribute('idMunicipi', lightning['idMunicipi'])
    #TODO: We do not really wnow it data is in EPSG:4326 (WGS84) or
    # EPSG:4258 (ETRS89)
    etrs_geo = QgsCoordinateReferenceSystem(4258)
    tr = QgsCoordinateTransform(etrs_geo, QgsProject.instance().crs(), QgsProject.instance())
    point = QgsGeometry.fromPointXY(QgsPointXY(float(lightning['coordenades']['longitud']), float(lightning['coordenades']['latitud'])))
    point.transform(tr)
    # obtain the point coordinates
    (x, y) = point.asPoint()
    # get the ellipse axis
    a = float(lightning['ellipse']['eixMajor'])
    b = float(lightning['ellipse']['eixMenor'])
    # if minor axis is greater than major, it seems that the data provided is
    # incongruent, so it ts aproximated to a circle
    if b > a:
        b = a
    # sample the ellipose with 100 points to be smooth
    ds = (2 * numpy.pi) / 100
    # interpolate the ellipse at origin
    ids = arange(0, 2 * numpy.pi, ds)
    points = [(a * cos(ids), b * sin(ids)) for ids in arange(0, 2 * numpy.pi, ds)]
    # rotate the ellipse the provided angle geographical north referenced
    alpha = radians(float(lightning['ellipse']['angle']) + 90)
    points = [(p[0] * cos(alpha) - p[1] * sin(alpha), p[0] * sin(alpha) + p[1] * cos(alpha)) for p in points]
    # apply translation to the lightning point
    points = [(p[0] + x, p[1] + y) for p in points]
    # add geometry to the feature
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
        return (False, None)
    # Create a message.
    #TODO: There is a bug where that not show all the progressbar message that
    # is solved creating a new standard message just before
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
                return (False, None)
        progress.setValue((i * 100) // hours)
    iface.messageBar().clearWidgets()
    # Create layers
    lightnings_layer = CreateLightningsLayer('Point', tr('lightnings'))
    errors_layer = CreateLightningsLayer('Polygon', tr('lighning-measurement-error'))
    AddLayerInPosition(lightnings_layer, 1)
    AddLayerInPosition(errors_layer, 2)
    # All data has been downloaded merging all arrays
    lightnings = list()
    for _, lighning_list in results:
        lightnings.extend(lighning_list)
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
