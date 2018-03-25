# -*- coding: utf-8 -*-
import re, os, omdb
from config import configuration_manager as cfg
from printout import print_script_name as psn
from printout import print_color_between as pcb
from printout import print_error, print_success, print_warning
from printout import print_no_line as pnl

_config = cfg()

def print_log(string, category=None):
    script = os.path.basename(__file__)
    psn(script, "", endl=False) # Print script name
    if category == "error":
        print_error("Error: ", endl=False)
    if category == "warning":
        print_warning("Warning: ", endl=False)
    if string.find('[') >= 0 and string.find(']') > 0:
        pcb(string, "blue")
    else:
        print(string)

# Determine tv root path
def root_path():
    path = _config.get_setting("path", "tvroot")
    return path

def _show_path(show):
    return os.path.join(root_path(), show)

def _show_path_season(show, season):
    return os.path.join(_show_path(show), season)

def has_nfo(show):
    full_path = _show_path(show)
    if not os.path.exists(full_path):
        print_log("path {} does not exists".format(full_path), category="warning")
        return False
    for file in os.listdir(full_path):
        if file.endswith(".nfo"):
            return True
    return False

def get_season_folder_list(show):
    list = []
    for item in os.listdir(_show_path(show)):
        if os.path.isdir(_show_path_season(show, item)):
            list.append(str(item))
    return list

def get_episodes(show, season_folder_name):
    ep_list = []
    full_path = os.listdir(os.path.join(_show_path(show), season_folder_name))
    for item in full_path:
        if _is_vid_file(str(item)):
            ep_list.append(str(item))
    return ep_list

def _is_vid_file(file_string):
    if file_string.endswith(".mkv"):
        return True
    if file_string.endswith(".mp4"):
        return True
    if file_string.endswith(".avi"):
        return True
    return False

def omdb_search(show):
    folder = show['folder']
    print_log("searching OMDb for [ {} ] ".format(folder))
    if show['imdb'] is not None:
        print_log("using IMDb-id [ {} ] ".format(show['imdb']))

# Determine ds/tvpath from tv folder
def guess_ds_folder(folder):
    rgx = re.compile('\.[Ss]\d{2}')
    match = re.search(rgx, folder)
    if match:
        splits = folder.split(match[0])
        return splits[0].replace(".", " ")

# Determine season from tv folder
def guess_season(string):
    rgx = re.compile('[Ss]\d{2}')
    match = re.search(rgx, string)
    if match:
        return match[0]
    return None

# Determine season from tv folder
def guess_season_episode(string):
    rgx = re.compile('[Ss]\d{2}[Ee]\d{2}')
    match = re.search(rgx, string)
    if match:
        return match[0]
    return None
