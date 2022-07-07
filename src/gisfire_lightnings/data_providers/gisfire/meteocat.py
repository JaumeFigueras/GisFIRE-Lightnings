# -*- coding: utf-8 -*-

import datetime
import json
import requests
from requests import RequestException
from requests.auth import HTTPBasicAuth

from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtCore import pyqtSignal

from gisfire_meteocat_lib.classes.lightning import Lightning

from typing import Union
from typing import Dict
from typing import List

import traceback

class DownloadLightningsUsingMeteocat(QObject):

    finished: pyqtSignal = pyqtSignal()
    progress: pyqtSignal = pyqtSignal(int)
    data: pyqtSignal = pyqtSignal([list])
    requested_day: datetime.date
    base_url: str
    username: str
    gisfire_token: str
    meteocat_api_key: str
    epsg_id: int

    def __init__(self, requested_day: datetime.date, base_url: str, username: str, gisfire_token: str,
                 meteocat_api_key: str, epsg_id: int) -> None:
        super().__init__()
        self.requested_day = requested_day
        self.base_url = base_url
        self.username = username
        self.gisfire_token = gisfire_token
        self.meteocat_api_key = meteocat_api_key
        self.epsg_id = epsg_id

    def run(self):
        lightnings: List[Lightning] = self.download_lightnings()
        self.data.emit(lightnings)  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908
        self.finished.emit()  # noqa known issue https://youtrack.jetbrains.com/issue/PY-22908

    def download_lightnings(self) -> Union[List[Lightning], None]:
        year: int = self.requested_day.year
        month: int = self.requested_day.month
        day: int = self.requested_day.day
        headers: Dict[str, str] = {"X-Api-Key": "{0:}".format(self.meteocat_api_key)}
        auth: HTTPBasicAuth = HTTPBasicAuth(self.username, self.gisfire_token)
        url: str = "{}/v1/meteocat/lightning/{}/{}/{}?srid={}".format(self.base_url, year, month, day, self.epsg_id)
        try:
            response: requests.Response = requests.get(url, headers=headers, auth=auth)
            if response.status_code == 200:
                try:
                    json_data = json.loads(response.text, object_hook=Lightning.object_hook_gisfire)
                    return json_data
                except Exception as e:
                    print(e)
                    print(traceback.format_exc())
                    return list()
            else:
                return list()
        except RequestException as _:
            return list()
