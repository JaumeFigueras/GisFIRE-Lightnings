from qgis.core import QgsProject
from qgis.core import QgsVectorLayer
from qgis.core import QgsLayerTree
from qgis.core import QgsLayerTreeLayer
from qgis.PyQt.QtCore import QObject


def add_layer_in_position(layer: QgsVectorLayer, position: int) -> None:
    """
    Add a data layer in a certain position of the QGis legend. It is one indexed, the number 1 the top position of the
    legend.

    :param layer: data layer to be added in the QGis legend
    :type layer: qgis.core.QgsVectorLayer
    :param position: Position to display the layer in the legend
    :type position: int
    """
    current_project: QgsProject = QgsProject()
    current_project.instance().addMapLayer(layer, True)
    root: QgsLayerTree = current_project.instance().layerTreeRoot()
    node_layer: QgsLayerTreeLayer = root.findLayer(layer.id())
    node_clone: QgsLayerTreeLayer = node_layer.clone()
    parent: QObject = node_layer.parent()
    parent.insertChildNode(position, node_clone)
    parent.removeChildNode(node_layer)

