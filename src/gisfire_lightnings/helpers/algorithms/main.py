# -*- coding: utf-8 -*-

from scipy.spatial import distance
from itertools import groupby
import numpy as np
import copy as cp
from gisfire_meteocat_lib.classes.lightning import Lightning

from typing import List
from typing import Any
from typing import Dict
from typing import Tuple


def non_crossing_paths(distance_matrix, path, max_iterations=100):
    """Creates a path that approximates a TSP by searching a planar graph
    with a maximum iterations limit

    :param distance_matrix: a matrix containing the distances between all the
    elements inside that input path
    :type distance_matrix: float matrix (a standard python matrix)

    :param path: the starting instance of the path to follow, the first and last
    element are the same and its values are the indices of the distance matrix.
    :type path: int list

    :param max_iterations: the maximum iterations the approximation algorithm
    will perform
    :type max_iterations: int

    :return: a new list containing the best ordered path found
    :rtype: int list
    """
    # Create a new path copying its values
    path = path[:]
    for iteration in range(max_iterations):
        # check for changes variable
        swap = False
        # Get four consecutive points in the path (looping)
        for i2 in range(1, len(path) - 2):
            i1 = i2 - 1
            for i4 in range(i2 + 2, len(path)):
                i3 = i4 - 1
                # The minimum distance does not contain a crossing, so the mid-elements are swapped
                if distance_matrix[path[i1]][path[i2]] + distance_matrix[path[i3]][path[i4]] > distance_matrix[path[i1]][path[i3]] + distance_matrix[path[i2]][path[i4]]:
                    path[i2], path[i3] = path[i3], path[i2]
                    swap = True
        if not swap:
            # End if nothing has changed
            break
    return path


def greedy_clustering(lightnings: List[Lightning], eps: float = 2000.0) -> Tuple[List[Lightning], int]:
    """
    Search the possible groups of lightnings that are at maximum a certain (EPS) distance between them

    :param lightnings: a list of lightnings to process
    :type lightnings: List[Lightning]
    :param eps: the maximum euclidean (2-norm) distance between two lightnings that belong to the same group. The
    default value assume meters as distance units, but the function does not treat units.
    :type eps: float
    :return: a tuple with: 1. A new list (deep copied) of lightnings objects
    adding the cluster id where the lightning belongs and a neighbour list; 2. The number of clusters
    :rtype: tuple (list, int)
    """
    # Create the new data in the lightnings
    for lightning in lightnings:
        setattr(lightning, 'cluster', -1)
        setattr(lightning, 'neighbours', set())
    # Start the cluster count
    cluster_id = 0
    # Assign a cluster for all the lightnings
    for i in range(len(lightnings)):
        # If not assigned a cluster
        if lightnings[i].cluster < 0:
            # Search for all its neighbours
            for j in range(i, len(lightnings)):
                dist: float = distance.euclidean((lightnings[i].lon, lightnings[i].lat),
                                                 (lightnings[j].lon, lightnings[j].lat))
                if dist <= eps and lightnings[j].cluster < 0:
                    lightnings[i].neighbours.add(j)
            # Assign the same cluster to its neighbours
            for neighbour in lightnings[i].neighbours:
                lightnings[neighbour].cluster = cluster_id
            cluster_id += 1
    return lightnings, cluster_id


def get_centroids(lightnings: List[Lightning]):
    """
    Create a list of centroids from a lightning list once they have been clustered. The list contains the centroid
    information as well ass lightning references

    :param lightnings: a list of lightnings to process
    :type lightnings: lightnings list.
    :return: a list with all clusters. A cluster is a dictionary with its id, a list of points (lightnings) and its centroid
    :rtype: list
    """
    # Copy the lightnings list
    sorted_lightnings = lightnings[:]
    # Sort it by clusters
    sorted_lightnings.sort(key=lambda x: x.cluster)
    # Group the lightnings by its cluster assignment and create a list of all
    # the groups
    clusters = [{'id': k, 'elements': list(g)} for k, g in groupby(sorted_lightnings, key=lambda x: x.cluster)]
    for cluster in clusters:
        # Compute the centroid. Numpy is used because standard python do not
        # allow to sum matrix columns by default
        cluster_points = np.array([(lightning.lon, lightning.lat) for lightning in cluster['elements']])
        length = cluster_points.shape[0]
        cluster['centroid'] = (np.sum(cluster_points[:, 0]) / length, np.sum(cluster_points[:, 1]) / length)
    return clusters


def re_arrange_clusters(clusters, lightnings: List[Lightning]) -> Tuple[List[Lightning], int]:
    """Create a new list (deep copied) of lightnings assiging to a cluster a
    lightning that is nearer to another cluster centroid that its own centroid

    :param clusters: a list of clusters
    :type cluster: a list of clusters. A cluster is a dictionary with its id, a
    list of points (lightnings) and its centroid
    :param lightnings: a list of lightnings to process
    :type lightnings: lightnings list. A lightning is an object (dictionary)
    with the information retrieved from the API and its cluster assignment

    :return: a tuple with a list with all lightnings with its new cluster
    assignment and the number of re-assignments. The clusters are not
    recalculated, it is necessarty to call the GetCentroids function to get the
    list of clusters with its new centroid
    :rtype: tuple of (lightnings list, number of changes)
    """
    # TODO: Què passa si acabo treient tots els llamps d'un cluster?
    changes: int = 0
    for lightning in lightnings:
        # Calculate the distance to its centroid
        dist = distance.euclidean((lightning.lon, lightning.lat), clusters[lightning.cluster]['centroid'])
        for cluster in clusters:
            # Calculate the distance to all centroids
            new_dist = distance.euclidean((lightning.lon, lightning.lat), cluster['centroid'])
            if new_dist < dist:
                # re-assign if it is nearer
                lightning.cluster = cluster['id']
                changes += 1
    return lightnings, changes


def compute_distance_matrix(points):
    """Computes a distance matrix from all the points in a list.

    :param points: a list of n-dimensional points
    :type points: list of lists

    :return: a symmetric distance matrix
    :rtype: matrix
    """
    pts = list()
    for pt in points:
        pts.append(np.asarray(pt))
    dist_matrix = np.zeros((len(points), len(points)))
    for i in range(0, len(pts)):
        dist_matrix[i][i] = 0.0
        for j in range(i+1, len(pts)):
            dist = np.linalg.norm(pts[i] - pts[j])
            dist_matrix[i][j] = dist
            dist_matrix[j][i] = dist
    return dist_matrix

