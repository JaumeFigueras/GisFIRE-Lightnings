# -*- coding: utf-8 -*-

from qgis.PyQt import uic
import os.path


def get_ui_class(plugin_dir, ui_file_name):
    """
    TODO

    :param plugin_dir:
    :type plugin_dir:
    :param ui_file_name:
    :type ui_file_name:
    :return:
    :rtype:
    """
    ui_file_path = plugin_dir + '/' + ui_file_name
    if os.path.exists(ui_file_path):
        return uic.loadUiType(ui_file_path)[0]
    else:
        return None
