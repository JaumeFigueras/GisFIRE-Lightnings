import numpy as np
from scipy.spatial import distance as dst

def ComputeDistanceMatrix(points):
    return dst.cdist(points, points, 'euclidean')
