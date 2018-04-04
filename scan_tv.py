# -*- coding: utf-8 -*-
import paths
import filetools as ftool
import tvshow as tvtool
import db_tv
import datetime, argparse, os
from printout import print_class as pr

pr = pr(os.path.basename(__file__))
db = db_tv.database()
if not db.load_success():
    quit()

tv_root = tvtool.root_path()
shows = os.listdir(tv_root)
shows.sort()
new_count = 0

# Add new episode, from filename, show as dict, season/episode as strings
def new_episode(show, season, ep_file_name):
    episode = { 'file' : ep_file_name, 'status' : "ok" }
    episode['date_scanned'] = datetime.datetime.now().strftime("%d %b %Y")
    episode['se'] = tvtool.guess_season_episode(episode['file'])
    episode['subs'] = {
        'sv' : tvtool.has_subtitle(show, ep_file_name, "sv"),
        'en' : tvtool.has_subtitle(show, ep_file_name, "en") }
    episode['omdb'] = tvtool.omdb_search_episode(show, season, episode['file'])
    pr.info(f"Adding new episode: {episode['se']} : {episode['file']}")
    return episode

def new_season(show, season):
    season = { 'folder' : season }
    season['omdb'] = tvtool.omdb_search_season(show, season['folder'])
    season['episodes'] = []
    return season

# Add new show to database
def new_show(folder):
    show = { 'folder' : folder }
    pr.info(f"found new show [{folder}] !")
    fp = os.path.join(tv_root, folder)
    date = ftool.get_creation_date(fp, convert=True)
    show['date_created'] = date.strftime("%d %b %Y") if date is not None else None
    show['date_scanned'] = datetime.datetime.now().strftime("%d %b %Y")
    show['status'] = "ok"
    show['seasons'] = []
    show['nfo'] = tvtool.has_nfo(folder)
    show['imdb'] = tvtool.nfo_to_imdb(folder)
    show['omdb'] = tvtool.omdb_search_show(show)
    for s in tvtool.get_season_folder_list(folder):
        season = { 'folder' : s, 'status' : "ok" }
        season['omdb'] = tvtool.omdb_search_season(show, season['folder'])
        season['episodes'] = []
        show['seasons'].append(season)
        for e in tvtool.get_episodes(folder, s):
            episode = new_episode(show, s, e)
            season['omdb'] = tvtool.omdb_search_season(show, season['folder'])
            season['episodes'].append(episode)
    pr.info(f"added [{folder}] to database!")
    db.add(show)

parser = argparse.ArgumentParser(description='tv scanner')
parser.add_argument('-m', '--max', dest='max', default=None,
    help='max new shows to scan')
args = parser.parse_args()

new_show_count = 0
new_episode_count = 0

try:
    max_scan = int(args.max)
    pr.info(f"will scan max {max_scan} new shows")
except:
    max_scan = None

# Scan for new shows...
for show in shows:
    if show.startswith("@"): # Diskstation
        continue;
    if max_scan and new_show_count >= max_scan:
        pr.info("max new show scan limit reached! breaking")
        break;
    pr.info(f"scanning [{show}]")
    if not db.exists(show):
        new_show(show)
        new_show_count += 1
        continue; # new_show() adds all new eps and seasons
    seasons = tvtool.get_season_folder_list(show)
    for season in seasons:
        episodes = tvtool.get_episodes(show, season)
        for ep in episodes:
            if not db.has_ep(show, ep):
                new_episode_count += 1
                show_object = db.data(show)
                episode_object = new_episode(show_object, season, ep)
                if not db.has_season(show, season):
                    season_object = new_season(show_object, season)
                    db.add_season(show, season_object)
                db.add_ep(show, season, episode_object)

pr.info("done scanning!")
pr.info(f"found {new_show_count} new shows.")
pr.info(f"found {new_episode_count} new episodes.")
if new_show_count > 0 or new_episode_count > 0:
    db.save()
    ftool.copy_dbs_to_webserver("tv")
