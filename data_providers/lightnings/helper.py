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

def AddLayerInPosition(layer, position):
    """Add a data layer in a certain position in the QGis legend. It is one
    indexed, beein the number 1 the top position of the legend.

    :param layer: data layer to be added in the QGis legend
    :type type: qgis.core.QgsVectorLayer

    :param name: one-indexed poition to add the layer
    :type name: int
    """
    QgsProject.instance().addMapLayer(layer, True)
    root = QgsProject.instance().layerTreeRoot()
    node_layer = root.findLayer(layer.id())
    node_clone = node_layer.clone()
    parent = node_layer.parent()
    parent.insertChildNode(position, node_clone)
    parent.removeChildNode(node_layer)
