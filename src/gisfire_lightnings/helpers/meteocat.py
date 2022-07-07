# -*- coding: utf-8 -*-
import numpy
from numpy import arange
from math import sin
from math import cos
from math import radians

from qgis.core import QgsVectorLayer
from qgis.core import QgsVectorDataProvider
from qgis.core import QgsField
from qgis.core import QgsProject
from qgis.core import QgsCoordinateReferenceSystem
from qgis.core import QgsFeature
from qgis.core import QgsPointXY
from qgis.core import QgsGeometry
from qgis.PyQt.QtCore import QVariant

from gisfire_meteocat_lib.classes.lightning import Lightning

from typing import Union
from typing import List


def create_lightnings_layer(layer_type: str, name: str, epsg_id: int) -> Union[QgsVectorLayer, None]:
    """
    Create a QGis vector layer with the attributes specified by the meteo.cat API definition

    :param layer_type: defines the feature type of the layer, meteo.cat provides information to construct a point layer
    or a polygon layer
    :type layer_type: string with two possible values 'Point' or 'Polygon'
    :param name: name of the layer that will be shown in the QGis legend
    :type name: string
    :return: the function returns the newly created layer or None depending on the correct feature type provided
    :rtype: qgis.core.QgsVectorLayer or None
    """
    # Check allowed feature types
    if layer_type != 'Point' and layer_type != 'Polygon':
        return None
    # Create the layer
    vl: QgsVectorLayer = QgsVectorLayer(layer_type, name, 'memory')
    pr: QgsVectorDataProvider = vl.dataProvider()
    # add fields
    attributes: List[QgsField] = [QgsField('id', QVariant.String),
                                  QgsField('meteocat_id', QVariant.String),
                                  QgsField('date', QVariant.String),
                                  QgsField('peak_current', QVariant.Double),
                                  QgsField('chi_squared', QVariant.Double),
                                  QgsField('ellipse_major_axis', QVariant.Double),
                                  QgsField('ellipse_minor_axis', QVariant.Double),
                                  QgsField('ellipse_angle', QVariant.Double),
                                  QgsField('number_of_sensors', QVariant.Int),
                                  QgsField('hit_ground', QVariant.Int)]
    pr.addAttributes(attributes)
    vl.updateFields()  # tell the vector layer to fetch changes from the provider
    # Assign current project CRS
    crs = QgsCoordinateReferenceSystem("EPSG:{:d}".format(epsg_id))
    vl.setCrs(crs, True)
    # Update layer's extent because change of extent in provider is not
    # propagated to the layer
    vl.updateExtents()
    return vl


def add_lightning_point(layer: QgsVectorLayer, lightning: Lightning) -> None:
    """
    Add a lightning location with its information to the point layer provided

    :param layer: data layer where the lightning will be added
    :type layer: qgis.core.QgsVectorLayer
    :param lightning: data object provided with lightning information
    :type lightning: Lightning
    """
    # create the feature
    feat = QgsFeature(layer.fields())
    # add attributes
    feat.setAttribute('id', str(lightning.id))
    feat.setAttribute('meteocat_id', str(lightning.meteocat_id))
    feat.setAttribute('date', lightning.date.strftime("%Y-%m-%d %H:%M:%S"))
    feat.setAttribute('peak_current', float(lightning.peak_current))
    feat.setAttribute('chi_squared', float(lightning.chi_squared))
    feat.setAttribute('ellipse_major_axis', float(lightning.ellipse_major_axis))
    feat.setAttribute('ellipse_minor_axis', float(lightning.ellipse_minor_axis))
    feat.setAttribute('ellipse_angle', float(lightning.ellipse_angle))
    feat.setAttribute('number_of_sensors', int(lightning.number_of_sensors))
    feat.setAttribute('hit_ground', 1 if lightning.hit_ground else 0)
    point: QgsGeometry = QgsGeometry.fromPointXY(QgsPointXY(float(lightning.x), float(lightning.y)))
    feat.setGeometry(point)
    layer.dataProvider().addFeature(feat)


def add_lightning_polygon(layer: QgsVectorLayer, lightning: Lightning) -> None:
    """
    Add a lightning error ellipse location with its information to the
    polygon layer provided

    :param layer: data layer where the lightning error ellipse will be added
    :type layer: qgis.core.QgsVectorLayer
    :param lightning: data object provided by meteo.cat with lightning information
    :type lightning: Lightning
    """
    # create the feature
    feat = QgsFeature(layer.fields())
    # add attributes
    feat.setAttribute('id', str(lightning.id))
    feat.setAttribute('meteocat_id', str(lightning.meteocat_id))
    feat.setAttribute('date', lightning.date.strftime("%Y-%m-%d %H:%M:%S"))
    feat.setAttribute('peak_current', lightning.peak_current)
    feat.setAttribute('chi_squared', lightning.chi_squared)
    feat.setAttribute('ellipse_major_axis', lightning.ellipse_major_axis)
    feat.setAttribute('ellipse_minor_axis', lightning.ellipse_minor_axis)
    feat.setAttribute('ellipse_angle', lightning.ellipse_angle)
    feat.setAttribute('number_of_sensors', lightning.number_of_sensors)
    feat.setAttribute('hit_ground', 1 if lightning.hit_ground else 0)
    # Get the point
    x, y = lightning.x, lightning.y
    # Get the ellipse axis
    a = lightning.ellipse_major_axis
    b = lightning.ellipse_minor_axis
    # If minor axis is greater than major, it seems that the data provided is incongruent, so it ts approximated to a
    # circle
    if b > a:
        b = a
    # Sample the ellipse with 100 points to be smooth
    ds = (2 * numpy.pi) / 100
    # interpolate the ellipse at origin
    ids = arange(0, 2 * numpy.pi, ds)
    points = [(a * cos(ids), b * sin(ids)) for ids in arange(0, 2 * numpy.pi, ds)]
    # rotate the ellipse the provided angle geographical north referenced
    alpha = radians(lightning.ellipse_angle + 90)
    points = [(p[0] * cos(alpha) - p[1] * sin(alpha), p[0] * sin(alpha) + p[1] * cos(alpha)) for p in points]
    # apply translation to the lightning point
    points = [(p[0] + x, p[1] + y) for p in points]
    # add geometry to the feature
    ellipse = [QgsPointXY(p[0], p[1]) for p in points]
    feat.setGeometry(QgsGeometry.fromPolygonXY([ellipse]))
    layer.dataProvider().addFeature(feat)
