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

import numpy as np
from scipy.spatial import distance as dst

def ComputeDistanceMatrix(points):
    """Computes a distance matrix from all the points in a list.

    :param points: a list of n-dimensional points
    :type points: list of lists

    :return: a symetric distance matrix
    :type return: matrix
    """
    return dst.cdist(points, points, 'euclidean')
