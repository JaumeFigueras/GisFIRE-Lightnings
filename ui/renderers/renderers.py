from qgis.core import QgsRuleBasedRenderer
from qgis.core import QgsCategorizedSymbolRenderer
from qgis.core import QgsRendererCategory
from qgis.core import QgsSymbol
from qgis.core import QgsMarkerSymbol
from qgis.core import QgsUnitTypes

from PyQt5.QtGui import QColor

def SetLightningsRenderer(layer, tr):
    # Create a default rule renderer to build a new one
    symbol = QgsSymbol.defaultSymbol(layer.geometryType())
    renderer = QgsRuleBasedRenderer(symbol)
    root = renderer.rootRule()
    # Create positive Rule
    rule_positive = root.children()[0].clone()
    rule_positive.setLabel(tr('Positive'))
    rule_positive.setFilterExpression('"_correntPic" >= 0 AND "_nuvolTerra" = 1')
    symbol = QgsMarkerSymbol.createSimple({'name': 'cross'})
    symbol.setSize(4.0)
    symbol.setSizeUnit(QgsUnitTypes.RenderMillimeters)
    symbol.setColor(QColor('#ff0000'))
    symbol.symbolLayer(0).setStrokeWidth(1.0)
    rule_positive.setSymbol(symbol)
    root.appendChild(rule_positive)
    # Create negative Rule
    rule_negative = root.children()[0].clone()
    rule_negative.setLabel(tr('Negative'))
    rule_negative.setFilterExpression('"_correntPic" < 0 AND "_nuvolTerra" = 1')
    symbol = QgsMarkerSymbol.createSimple({'name': 'line'})
    symbol.setAngle(90.0)
    symbol.setSize(4.0)
    symbol.setSizeUnit(QgsUnitTypes.RenderMillimeters)
    symbol.setColor(QColor('#00ff00'))
    symbol.symbolLayer(0).setStrokeWidth(1.0)
    rule_negative.setSymbol(symbol)
    root.appendChild(rule_negative)
    # Create positive Rule
    rule_cloudcloud = root.children()[0].clone()
    rule_cloudcloud.setLabel(tr('Cloud - Cloud'))
    rule_cloudcloud.setFilterExpression('"_nuvolTerra" = 0')
    symbol = QgsMarkerSymbol.createSimple({'name': 'circle'})
    symbol.setSize(1.0)
    symbol.setSizeUnit(QgsUnitTypes.RenderMillimeters)
    symbol.setColor(QColor('#0000ff'))
    rule_cloudcloud.setSymbol(symbol)
    rule_cloudcloud.setActive(False)
    root.appendChild(rule_cloudcloud)
    # Remove default
    root.removeChildAt(0)
    # set Renderer
    layer.setRenderer(renderer)

def SetClusterRenderer(layer, symbol_name, clusters, tr):
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
