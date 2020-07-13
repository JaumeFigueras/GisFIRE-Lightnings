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
