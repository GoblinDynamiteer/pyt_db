# -*- coding: utf-8 -*-
import re
from config import configuration_manager as cfg

_config = cfg()

# Determine tv root path
def root_path():
    path = _config.get_setting("path", "tvroot")
    return path

# Determine ds/tvpath from tv folder
def guess_ds_folder(folder):
    rgx = re.compile('\.[Ss]\d{2}')
    match = re.search(rgx, folder)
    if match:
        splits = folder.split(match[0])
        return splits[0].replace(".", " ")

# Determine season from tv folder
def guess_season(folder):
    rgx = re.compile('[Ss]\d{2}')
    match = re.search(rgx, folder)
    if match:
        return match[0]
    return None
