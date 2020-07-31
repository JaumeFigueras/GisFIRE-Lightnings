from scipy.spatial import distance
from itertools import groupby
import numpy as np
import copy as cp

def NonCrossingPaths(distance_matrix, path, max_iterations=100):
    path = path[:]
    for iter in range(max_iterations):
        swap = False
        for i2 in range(1, len(path) - 2):
            i1 = i2 - 1
            for i4 in range(i2 + 2, len(path)):
                i3 = i4 - 1
                if distance_matrix[path[i1]][path[i2]] + distance_matrix[path[i3]][path[i4]] > distance_matrix[path[i1]][path[i3]] + distance_matrix[path[i2]][path[i4]]:
                    path[i2], path[i3] = path[i3], path[i2]
                    swap = True
        if not swap:
            break
    return path

def GreedyClustering(lightnings, EPS=2000):
    lightnings = cp.deepcopy(lightnings)
    for lightning in lightnings:
        lightning['cluster'] = -1
        lightning['neighbours'] = set()
    cluster_id = 0
    for i in range(len(lightnings)):
        if lightnings[i]['cluster'] < 0:
            for j in range(i, len(lightnings)):
                dist = distance.euclidean(lightnings[i]['point'], lightnings[j]['point'])
                if dist <= EPS and lightnings[j]['cluster'] < 0:
                    lightnings[i]['neighbours'].add(j)
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
