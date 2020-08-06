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
