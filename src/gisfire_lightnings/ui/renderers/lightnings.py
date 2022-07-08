# -*- coding: utf-8 -*-

from qgis.core import QgsRuleBasedRenderer
from qgis.core import QgsCategorizedSymbolRenderer
from qgis.core import QgsRendererCategory
from qgis.core import QgsSymbol
from qgis.core import QgsMarkerSymbol
from qgis.core import QgsUnitTypes
from qgis.core import QgsVectorLayer

from PyQt5.QtGui import QColor

from typing import Callable
from typing import Any
from typing import List


def set_lightnings_renderer(layer: QgsVectorLayer, tr: Callable):
    """
    Set the rendering attributes for the lightnings.

    :param layer:
    :type layer:
    :param tr:
    :type tr:
    :return:
    :rtype:
    """
    # Create a default rule renderer to build a new one
    symbol: QgsSymbol = QgsSymbol.defaultSymbol(layer.geometryType())
    renderer: QgsRuleBasedRenderer = QgsRuleBasedRenderer(symbol)
    root: QgsRuleBasedRenderer.Rule = renderer.rootRule()
    # Create positive Rule
    rule_positive: QgsRuleBasedRenderer.Rule = root.children()[0].clone()
    rule_positive.setLabel(tr('Positive'))
    rule_positive.setFilterExpression('"peak_current" >= 0 AND "hit_ground" = 1')
    symbol: QgsMarkerSymbol = QgsMarkerSymbol.createSimple({'name': 'cross'})
    symbol.setSize(4.0)
    symbol.setSizeUnit(QgsUnitTypes.RenderMillimeters)
    symbol.setColor(QColor('#ff0000'))
    symbol.symbolLayer(0).setStrokeWidth(1.0)
    rule_positive.setSymbol(symbol)
    root.appendChild(rule_positive)
    # Create negative Rule
    rule_negative: QgsRuleBasedRenderer.Rule = root.children()[0].clone()
    rule_negative.setLabel(tr('Negative'))
    rule_negative.setFilterExpression('"peak_current" < 0 AND "hit_ground" = 1')
    symbol: QgsMarkerSymbol = QgsMarkerSymbol.createSimple({'name': 'line'})
    symbol.setAngle(90.0)
    symbol.setSize(4.0)
    symbol.setSizeUnit(QgsUnitTypes.RenderMillimeters)
    symbol.setColor(QColor('#00ff00'))
    symbol.symbolLayer(0).setStrokeWidth(1.0)
    rule_negative.setSymbol(symbol)
    root.appendChild(rule_negative)
    # Create positive Rule
    rule_cloud_to_cloud: QgsRuleBasedRenderer.Rule= root.children()[0].clone()
    rule_cloud_to_cloud.setLabel(tr('Cloud to Cloud'))
    rule_cloud_to_cloud.setFilterExpression('"hit_ground" = 0')
    symbol: QgsMarkerSymbol = QgsMarkerSymbol.createSimple({'name': 'circle'})
    symbol.setSize(1.0)
    symbol.setSizeUnit(QgsUnitTypes.RenderMillimeters)
    symbol.setColor(QColor('#0000ff'))
    rule_cloud_to_cloud.setSymbol(symbol)
    rule_cloud_to_cloud.setActive(True)
    root.appendChild(rule_cloud_to_cloud)
    # Remove default
    root.removeChildAt(0)
    # set Renderer
    layer.setRenderer(renderer)
    layer.triggerRepaint()


def set_cluster_renderer(layer: QgsVectorLayer, symbol_name: str, clusters: List[Any]):
    """
    Set the rendering attributes for the clusters.

    :param layer:
    :type layer:
    :param symbol_name:
    :type symbol_name:
    :param clusters:
    :type clusters:
    :return:
    :rtype:
    """
    categories = list()
    color_step = 256.0 / len(clusters)
    for i in range(len(clusters)):
        symbol = QgsMarkerSymbol.createSimple({'name': '{}'.format(symbol_name)})
        symbol.setSize(2.0)
        symbol.setSizeUnit(QgsUnitTypes.RenderMillimeters)
        symbol.setColor(QColor.fromHsv(0, 255 - int(i * color_step), 255))
        categories.append(QgsRendererCategory(i, symbol, 'Cluster #{:3}'.format(i)))
    categorized_renderer = QgsCategorizedSymbolRenderer('cluster', categories)
    layer.setRenderer(categorized_renderer)
    layer.triggerRepaint()

