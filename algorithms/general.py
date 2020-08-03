from scipy.spatial import distance
from itertools import groupby
import numpy as np
import copy as cp

def NonCrossingPaths(distance_matrix, path, max_iterations=100):
    """Creates a path that aproximates a TSP by searching a planar graph
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

    :return: a new list conaining the best ordered path found
    :type return: int list
    """
    # Create a new path copying its values
    path = path[:]
    for iter in range(max_iterations):
        # check for changes variable
        swap = False
        # Get four consecutive points in the path (looping)
        for i2 in range(1, len(path) - 2):
            i1 = i2 - 1
            for i4 in range(i2 + 2, len(path)):
                i3 = i4 - 1
                # The minim distance does not contain a crossing, so the mid elements are swaped
                if distance_matrix[path[i1]][path[i2]] + distance_matrix[path[i3]][path[i4]] > distance_matrix[path[i1]][path[i3]] + distance_matrix[path[i2]][path[i4]]:
                    path[i2], path[i3] = path[i3], path[i2]
                    swap = True
        if not swap:
            # End if nothing has changed
            break
    return path

def GreedyClustering(lightnings, EPS=2000.0):
    """Search the possible groups of lightnings that are at maximum an certain
    (EPS) distance between them

    :param lightnings: a list of lightnings to process
    :type lightnings: lightnings list. A lightning is an object (dictionary)
    with the information retrieved from the API

    :param EPS: the maximum euclidean (2-norm) distance between two lightnings
    that belong to the same group. The default value assume meters as distance
    units, but the function does not treat units.
    :type EPS: float

    :return: a tuple with: 1. A new list (deep copied) of lightnings objects
    adding the cluster id where the lightning belongs and a neighbour list; 2.
    The number of clusters
    :type return: tuple (list, int)
    """
    # Copy the lightning list
    lightnings = cp.deepcopy(lightnings)
    # Create the new data in the lightnings
    for lightning in lightnings:
        lightning['cluster'] = -1
        lightning['neighbours'] = set()
    # Start the cluster count
    cluster_id = 0
    # Assign a cluster for all the lightnings
    for i in range(len(lightnings)):
        # If not assigned a cluster
        if lightnings[i]['cluster'] < 0:
            # Search for all its neighbours
            for j in range(i, len(lightnings)):
                dist = distance.euclidean(lightnings[i]['point'], lightnings[j]['point'])
                if dist <= EPS and lightnings[j]['cluster'] < 0:
                    lightnings[i]['neighbours'].add(j)
            # Assign the same cluster to its neighbours
            for neighbour in lightnings[i]['neighbours']:
                lightnings[neighbour]['cluster'] = cluster_id
            cluster_id += 1
    return (lightnings, cluster_id)

def GetCentroids(lightnings):
    sorted_lightnings = lightnings[:]
    sorted_lightnings.sort(key=lambda x: x['cluster'])
    clusters = [{'id': k, 'points': list(g)} for k, g in groupby(sorted_lightnings, key=lambda x: x['cluster'])]
    for cluster in clusters:
        cluster_points = np.array([(pt['point'][0], pt['point'][1]) for pt in cluster['points']])
        length = cluster_points.shape[0]
        cluster['centroid'] = (np.sum(cluster_points[:, 0]) / length, np.sum(cluster_points[:, 1]) / length)
    return clusters

def ReArrangeClusters(clusters, points):
    points = cp.deepcopy(points)
    changes = 0
    for point in points:
        dist = distance.euclidean(point['point'], clusters[point['cluster']]['centroid'])
        for cluster in clusters:
            new_dist = distance.euclidean(point['point'], cluster['centroid'])
            if new_dist < dist:
                point['cluster'] = cluster['id']
                changes += 1
    return (points, changes)
