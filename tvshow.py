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

def __omdb_search(show_d, season_n = None, episode_n = None):
    folder = show_d['folder']
    query = None
    if show_d['imdb']:
        query = show_d['imdb']
    else:
        query = show_d['folder']
    pr.info("searching omdb for [{}] ".format(show_d['folder']), end_line=False)
    pr.color_brackets(" as [{}] ".format(query), "green", end_line=False)
    if season_n:
        pr.output("-season {}".format(season_n), end_line=False)
    if episode_n:
        pr.output(" -episode {}".format(episode_n), end_line=False)
    search = omdb.omdb_search(query, season=season_n, episode=episode_n)
    data = search.data()
    try:
        if data['Response'] == "False":
            pr.color_brackets(" [response false]!", "yellow")
            return None
        pr.color_brackets(" [got data]!", "green")
        return data
    except:
        pr.color_brackets(" [script error] !", "red")
        return None

def omdb_search_show(show_d, season_n = None, episode_n = None):
    return __omdb_search(show_d, season_n=season_n, episode_n=episode_n)

def omdb_search_season(show_d, season_s, episode_n=None):
    rgx = re.compile('\d{2}$')
    match_season_n = re.search(rgx, season_s)
    if match_season_n:
        return omdb_search_show(show_d, season_n=int(match_season_n[0]), episode_n=episode_n)

def omdb_search_episode(show_d, season_s, episode_s):
    rgx = re.compile('[Ss]\d{2}[Ee]\d{2}')
    match = re.search(rgx, episode_s)
    if match:
        rgx = re.compile('[Ee]\d{2}')
        match = re.search(rgx, match[0])
        if match:
            rgx = re.compile('\d{2}')
            match_episode_n = re.search(rgx, match[0])
            if match_episode_n:
                return omdb_search_season(show_d, season_s=season_s, episode_n=int(match_episode_n[0]))
