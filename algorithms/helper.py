import numpy as np
from scipy.spatial import distance as dst

def Layer2Vector(layer):
    return [(feat.geometry().asPoint().x(), feat.geometry().asPoint().y()) for feat in layer.getFeatures()]

def ComputeDistanceMatrix(points):
    return dst.cdist(points, points, 'euclidean')
