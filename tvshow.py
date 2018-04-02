# -*- coding: utf-8 -*-
import re, os, omdb
from config import configuration_manager as cfg
from printout import print_class as pr
import filetools as ftool

pr = pr(os.path.basename(__file__))
_config = cfg()

# Determine tv root path
def root_path():
    path = _config.get_setting("path", "tvroot")
    return path

def show_obj_to_str(obj_to_check):
    if isinstance(obj_to_check, str):
        return obj_to_check
    pr.warning("converting show object to string")
    return obj_to_check['folder']

def show_str_to_obj(str_to_check):
    if not isinstance(str_to_check, str):
        return str_to_check
    pr.warning("converting show string to object")
    return obj_to_check['folder']

def _show_path(show):
    show = show_obj_to_str(show)
    return os.path.join(root_path(), show)

def _show_path_season(show, season):
    show = show_obj_to_str(show)
    return os.path.join(_show_path(show), season)

def has_nfo(show):
    show = show_obj_to_str(show)
    full_path = _show_path(show)
    if not os.path.exists(full_path):
        pr.warning("path {} does not exists".format(full_path))
        return False
    for file in os.listdir(full_path):
        if file.endswith(".nfo"):
            return True
    return False

def add_nfo_manual(show, replace=False):
    show = show_obj_to_str(show)
    path = _show_path(show)
    pr.info("add imdb-id for [{}]: ".format(show), end_line=False)
    imdb_input = input("")
    re_imdb = re.compile("tt\d{1,}")
    imdb_id = re_imdb.search(imdb_input)
    if imdb_id:
        id = imdb_id.group(0)
        ftool.create_nfo(path, id, "tv", replace)

# Get files for movie
def _get_file(path, file_ext, full_path = False):
    for file in os.listdir(path):
        if file.endswith("." + file_ext):
            return os.path.join(path, str(file)) if full_path else str(file)
    return None

# Extract IMDb-id from nfo
def nfo_to_imdb(show):
    show = show_obj_to_str(show)
    if not has_nfo(show):
        return None
    f = open(_get_file(_show_path(show), "nfo", full_path = True), "r")
    imdb_url = f.readline()
    f.close()
    re_imdb = re.compile("tt\d{1,}")
    imdb_id = re_imdb.search(imdb_url)
    return imdb_id.group(0) if imdb_id else None

def get_season_folder_list(show):
    list = []
    for item in os.listdir(_show_path(show)):
        if os.path.isdir(_show_path_season(show, item)):
            list.append(str(item))
    return list

def get_episodes(show, season_folder_name):
    show = show_obj_to_str(show)
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

# Determine ds/tvpath from tv folder
def guess_ds_folder(show):
    show = show_obj_to_str(show)
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

def __omdb_search(query, se = None, ep = None):
    pr.info("searching omdb for {}".format(query))
    search = omdb.omdb_search(query, season=se, episode=ep)
    data = search.data()
    try:
        if data['Response'] == "False":
            pr.warning("response false!")
            return None
        pr.info("got data!")
        return data
    except:
        pr.warning("omdb search script error!")
        return None

def omdb_search_show(show_object, season = None, episode = None):
    folder = show_object['folder']
    query = None
    if show_object['imdb'] is not None:
        query = show_object['imdb']
    else:
        query = show_object['folder']
    return __omdb_search(query, se=season, ep=episode)

def omdb_search_season(show, season, episode=None):
    rgx = re.compile('\d{2}$')
    match = re.search(rgx, season)
    if match:
        return omdb_search_show(show, season=int(match[0]), episode=episode)

def omdb_search_episode(show, season, episode):
    rgx = re.compile('[Ss]\d{2}[Ee]\d{2}')
    match = re.search(rgx, episode)
    if match:
        rgx = re.compile('[Ee]\d{2}')
        match = re.search(rgx, match[0])
        if match:
            rgx = re.compile('\d{2}')
            ep = re.search(rgx, match[0])
            if ep:
                return omdb_search_season(show, season=season, episode=ep[0])
