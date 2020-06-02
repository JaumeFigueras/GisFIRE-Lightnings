import time
import datetime
import concurrent.futures

from qgis.PyQt.QtWidgets import QProgressBar
from qgis.PyQt.QtCore import *
from qgis.core import Qgis
from qgis.gui import QgsMessageBar

def download_thread(date, hour):
    print("{}, {}".format(date,hour))
    time.sleep(0.25)
    return True

def download_lightning_data(iface, tr, day):
    iface.messageBar().pushMessage("", tr("Downloading Meteo.cat Lightning data."), level=Qgis.Info, duration=1)
    progressMessageBar = iface.messageBar().createMessage(tr("Downloading Meteo.cat Lightning data."))
    progress = QProgressBar()
    progress.setMaximum(100)
    progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
    progressMessageBar.layout().addWidget(progress)
    iface.messageBar().pushWidget(progressMessageBar, Qgis.Info)

    today = datetime.datetime.utcnow().date()
    diff = today - day
    if diff.days > 0:
        hours = 24
    else:
        now = datetime.datetime.utcnow()
        hours = now.hour
    print(hours)
    for i in range(hours):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(download_thread, day, i)
            return_value = future.result()
            print(return_value)
        progress.setValue((i * 100) // hours)

    iface.messageBar().clearWidgets()
