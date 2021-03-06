# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GisFIRELightnings
                                 A QGIS plugin
 GisFIRE module to manage lightning information, clustering and routing for
 wildfire surveillance
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-05-20
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Jaume Figueras
        email                : jaume.figueras@upc.edu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation version 3                                *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.core import QgsProject
from qgis.core import QgsVectorLayer
from qgis.core import QgsField
from qgis.core import QgsGeometry
from qgis.core import QgsFeature
from qgis.core import QgsPointXY

from PyQt5.QtCore import QVariant

def CreateClusteredPointsLayer(name):
    """Create a QGis vector layer with the lightning information adding the
    clustering assignment

    :param name: name of the layer that will be shown in the QGis legend
    :type name: string

    :return: the function returns the newly created layer
    :type return: qgis.core.QgsVectorLayer or None
    """
    # create layer
    vl = QgsVectorLayer('Point', name, 'memory')
    pr = vl.dataProvider()
    # add fields
    attributes = [QgsField('id',  QVariant.Int),
                    QgsField('cluster',  QVariant.Int),
                    QgsField('_id',  QVariant.String),
                    QgsField('_data',  QVariant.String),
                    QgsField('_correntPic',  QVariant.Double),
                    QgsField('_chi2',  QVariant.Double),
                    QgsField('_ellipse_eixMajor',  QVariant.Double),
                    QgsField('_ellipse_eixMenor',  QVariant.Double),
                    QgsField('_ellipse_angle',  QVariant.Double),
                    QgsField('_numSensors',  QVariant.Int),
                    QgsField('_nuvolTerra',  QVariant.Int),
                    QgsField('_idMunicipi',  QVariant.String),
                    QgsField('_lon',  QVariant.Double),
                    QgsField('_lat',  QVariant.Double)]
    pr.addAttributes(attributes)
    vl.updateFields() # tell the vector layer to fetch changes from the provider
    # Assign current project CRS
    crs = QgsProject.instance().crs()
    vl.setCrs(crs, True)
    # Update layer's extent because change of extent in provider is not
    # propagated to the layer
    vl.updateExtents()
    return vl

def AddClusteredLightningPoint(layer, lightning):
    """Add a lightning location with its information to the point layer provided

    :param layer: data layer where the lightning will be added
    :type type: qgis.core.QgsVectorLayer

    :param name: data object provided  with lightning information
    :type name: object
    """
    # create the feature
    feat = QgsFeature(layer.fields())
    # add attributes
    feat.setAttribute('id', lightning['id'])
    feat.setAttribute('cluster', lightning['cluster'])
    feat.setAttribute('_id', lightning['_id'])
    feat.setAttribute('_data', lightning['_data'])
    feat.setAttribute('_correntPic', lightning['_correntPic'])
    feat.setAttribute('_chi2', lightning['_chi2'])
    feat.setAttribute('_ellipse_eixMajor', lightning['_ellipse_eixMajor'])
    feat.setAttribute('_ellipse_eixMenor', lightning['_ellipse_eixMenor'])
    feat.setAttribute('_ellipse_angle', lightning['_ellipse_angle'])
    feat.setAttribute('_numSensors', lightning['_numSensors'])
    feat.setAttribute('_nuvolTerra', lightning['_nuvolTerra'])
    feat.setAttribute('_idMunicipi', lightning['_idMunicipi'])
    feat.setAttribute('_lon', lightning['_lon'])
    feat.setAttribute('_lat', lightning['_lat'])
    geom = QgsGeometry.fromPointXY(QgsPointXY(lightning['point'][0], lightning['point'][1]))
    feat.setGeometry(geom)
    layer.dataProvider().addFeature(feat)

def CreateCentroidsPointsLayer(name):
    """Create a QGis vector layer with the centroid information of each
    lightning cluster

    :param name: name of the layer that will be shown in the QGis legend
    :type name: string

    :return: the function returns the newly created layer
    :type return: qgis.core.QgsVectorLayer or None
    """
    # create layer
    vl = QgsVectorLayer('Point', name, 'memory')
    pr = vl.dataProvider()
    # add fields
    attributes = [QgsField('id',  QVariant.Int),
                    QgsField('cluster',  QVariant.Int)]
    pr.addAttributes(attributes)
    vl.updateFields() # tell the vector layer to fetch changes from the provider
    # Assign current project CRS
    crs = QgsProject.instance().crs()
    vl.setCrs(crs, True)
    # Update layer's extent because change of extent in provider is not
    # propagated to the layer
    vl.updateExtents()
    return vl

def AddCentroidPoint(layer, cluster):
    """Add a centroid location with its information to the point layer provided

    :param layer: data layer where the lightning will be added
    :type type: qgis.core.QgsVectorLayer

    :param cluster: data object provided  with lightning information
    :type cluster: object
    """
    # create the feature
    feat = QgsFeature(layer.fields())
    # add attributes
    feat.setAttribute('id', cluster['id'])
    feat.setAttribute('cluster', cluster['id'])
    geom = QgsGeometry.fromPointXY(QgsPointXY(cluster['centroid'][0], cluster['centroid'][1]))
    feat.setGeometry(geom)
    layer.dataProvider().addFeature(feat)

def CreatePathLayer(type, name):
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
    if type != 'Point' and type != 'LineString':
        return None
    # create layer
    vl = QgsVectorLayer(type, name, 'memory')
    pr = vl.dataProvider()
    # add fields
    attributes = [QgsField('_id',  QVariant.Int)]
    pr.addAttributes(attributes)
    vl.updateFields() # tell the vector layer to fetch changes from the provider
    # Assign current project CRS
    crs = QgsProject.instance().crs()
    vl.setCrs(crs, True)
    # Update layer's extent because change of extent in provider is not
    # propagated to the layer
    vl.updateExtents()
    return vl

def AddPathPoint(layer, point):
    """Add a lightning location with its information to the point layer provided

    :param layer: data layer where the lightning will be added
    :type type: qgis.core.QgsVectorLayer

    :param name: data object provided by meteo.cat with lightning information
    :type name: object
    """
    # create the feature
    feat = QgsFeature(layer.fields())
    # add attributes
    feat.setAttribute('_id', point['id'])
    geom = QgsGeometry.fromPointXY(QgsPointXY(point['x'], point['y']))
    feat.setGeometry(geom)
    layer.dataProvider().addFeature(feat)

def AddPathLine(layer, points):
    """Add a lightning location with its information to the point layer provided

    :param layer: data layer where the lightning will be added
    :type type: qgis.core.QgsVectorLayer

    :param name: data object provided by meteo.cat with lightning information
    :type name: object
    """
    # create the feature
    feat = QgsFeature(layer.fields())
    # add attributes
    feat.setAttribute('_id', 0)
    line = list()
    for i in range(len(points)):
        line.append(QgsPointXY(points[i]['x'], points[i]['y']))
    geom = QgsGeometry.fromPolylineXY(line)
    feat.setGeometry(geom)
    layer.dataProvider().addFeature(feat)
