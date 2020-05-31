import time
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.PyQt.QtCore import *
from qgis.core import Qgis
from qgis.gui import QgsMessageBar

def download_lightning_data(iface, tr, day):
    iface.messageBar().pushMessage("", "Downloading Meteo.cat Lightning data.", level=Qgis.Info, duration=1)
    progressMessageBar = iface.messageBar().createMessage("Downloading Meteo.cat Lightning data.")
    progress = QProgressBar()
    progress.setMaximum(100)
    progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
    progressMessageBar.layout().addWidget(progress)
    iface.messageBar().pushWidget(progressMessageBar, Qgis.Info)

    for i in range(24):
        time.sleep(0.25)
        progress.setValue((i * 100) // 24)

    iface.messageBar().clearWidgets()
