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

def ComputeDistanceMatrix(points):
    """Computes a distance matrix from all the points in a list.

    :param points: a list of n-dimensional points
    :type points: list of lists

    :return: a symetric distance matrix
    :type return: matrix
    """
    pts = list()
    for pt in points:
        pts.append(np.asarray(pt))
    dist_matrix = np.zeros((len(points), len(points)))
    for i in range(0, len(pts)):
        dist_matrix[i][i] = 0.0
        for j in range(i+1, len(pts)):
            distance = np.linalg.norm(pts[i] - pts[j])
            dist_matrix[i][j] = distance
            dist_matrix[j][i] = distance
    return dist_matrix
