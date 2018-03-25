# -*- coding: utf-8 -*-
import paths
import filetools as ftool
import tvshow as tvtool
import db_tv
from printout import print_blue, print_no_line, print_color_between
from printout import print_script_name as psn
from printout import print_color_between as pcb
from printout import print_error
import os
import datetime

db = db_tv.database()
if not db.load_success():
    quit()

tv_root = tvtool.root_path()
shows = os.listdir(tv_root)
shows.sort()
new_count = 0

# Print with script name as prefix
def print_log(string, category=None):
    script = os.path.basename(__file__)
    psn(script, "", endl=False) # Print script name
    if category == "error":
        print_error("Error: ", endl=False)
    if string.find('[') >= 0 and string.find(']') > 0:
        pcb(string, "blue")
    else:
        print(string)

# Add new episode, from filename
def new_episode(ep):
    episode = { 'file' : ep, 'status' : "ok" }
    episode['date_scanned'] = datetime.datetime.now().strftime("%d %b %Y")
    episode['se'] = tvtool.guess_season_episode(ep)
    print_log("Adding new episode: {} : {}".format(episode['se'], ep))
    return episode

# Add new show to database
def new_show(folder):
    show = { 'folder' : folder }
    print_log("found new show [ {} ] !".format(folder))
    fp = os.path.join(tv_root, folder)
    date = ftool.get_creation_date(fp, convert=True)
    show['date_created'] = date.strftime("%d %b %Y") if date is not None else None
    show['date_scanned'] = datetime.datetime.now().strftime("%d %b %Y")
    show['status'] = "ok"
    show['seasons'] = []
    for s in tvtool.get_season_folder_list(folder):
        season = { 'folder' : s }
        season['episodes'] = []
        show['seasons'].append(season)
        for e in tvtool.get_episodes(folder, s):
            episode = new_episode(e)
            season['episodes'].append(episode)
    show['nfo'] = tvtool.has_nfo(folder)
    print_log("added [ {} ] to database!".format(folder))
    db.add(show)

new_show_count = 0
new_episode_count = 0
# Scan for new shows...
for show in shows:
    if show.startswith("@"): # Diskstation
        continue;
    print_log("scanning [ {} ]".format(show))
    if not db.exists(show):
        new_show(show)
        new_show_count += 1
    seasons = tvtool.get_season_folder_list(show)
    for season in seasons:
        episodes = tvtool.get_episodes(show, season)
        for ep in episodes:
            if not db.has_ep(show, season, ep):
                new_episode_count += 1
                episode = new_episode(show, season, ep)
                db.add_ep(show, season, episode)

print_log("done scanning!")
print_log("found ({}) new shows.".format(new_show_count))
print_log("found ({}) new episodes.".format(new_episode_count))
if new_show_count > 0 or new_episode_count > 0:
    db.save()
    ftool.copy_dbs_to_webserver("tv")
