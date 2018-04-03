# -*- coding: utf-8 -*-
import paths, json, os, argparse
import db_tv as tv_database
import filetools as ftool
import tvshow as tvtool
from printout import print_class as pr

pr = pr(os.path.basename(__file__))
db = tv_database.database()
if not db.load_success():
    pr.error("database read error, quitting...")
    quit()

tv_root = tvtool.root_path()
shows = os.listdir(tv_root)
shows.sort()

def check_nfo():
    for show in shows:
        if show.startswith("@"): # Diskstation
            continue;
        if tvtool.has_nfo(show):
            if tvtool.nfo_to_imdb(show):
                pr.info("{} has tvshow.nfo".format(show))
            else:
                pr.warning("{} has non-imdb tvshow.nfo".format(show))
                tvtool.add_nfo_manual(show, replace=True)
        else:
            tvtool.add_nfo_manual(show)

def omdb_update():
    pr.info("trying to omdb-search for missing data")
    save_db = False
    success_count = 0
    for show_s in db.list_shows():
        show_d = db.data(show_s)
        if not show_d["omdb"]:
            omdb_result = tvtool.omdb_search_show(show_d)
            if omdb_result:
                show_d["omdb"] = omdb_result
                need_update = True
                save_db = True
                success_count += 1
        season_index = 0
        need_update = False
        for season_d in show_d["seasons"]:
            if not season_d["omdb"]:
                omdb_result = tvtool.omdb_search_season(show_d, season_d["folder"])
                if omdb_result:
                    show_d["seasons"][season_index]["omdb"] = omdb_result
                    need_update = True
                    save_db = True
                    success_count += 1
            episode_index = 0
            for episode_d in season_d["episodes"]:
                if not episode_d["omdb"]:
                    omdb_result = tvtool.omdb_search_episode(
                        show_d, season_d["folder"], episode_d["file"])
                    if omdb_result:
                        need_update = True
                        save_db = True
                        success_count += 1
                        show_d["seasons"][season_index]["episodes"][episode_index]["omdb"] = omdb_result
                episode_index += 1
            season_index +=1
        if need_update:
            db.update(show_d["folder"], show_d, key=None)
    pr.info("done!")
    if success_count > 0:
        pr.info("successfully updated omdb-data for {} items".format(success_count))
    if save_db:
        db.save()

def omdb_force_update(show_s):
    success_count = 0
    pr.info("force-updating omdb-data for {}".format(show_s))
    show_d = db.data(show_s)
    omdb_result = tvtool.omdb_search_show(show_d)
    show_d["omdb"] = omdb_result
    season_index = 0
    for season_d in show_d["seasons"]:
        omdb_result = tvtool.omdb_search_season(show_d, season_d["folder"])
        show_d["seasons"][season_index]["omdb"] = omdb_result
        episode_index = 0
        for episode_d in season_d["episodes"]:
            omdb_result = tvtool.omdb_search_episode(show_d, season_d["folder"], episode_d["file"])
            show_d["seasons"][season_index]["episodes"][episode_index]["omdb"] = omdb_result
            episode_index += 1
        season_index +=1
    db.update(show_d["folder"], show_d, key=None)
    db.save()

parser = argparse.ArgumentParser(description='TVDb tools')
parser.add_argument('func', type=str,
    help='TVDb command: maintain, checkdeleted, checknfo, omdbsearch, omdbforce')
parser.add_argument('--show', "-s", type=str, dest="show_s", default=None, help='show to process')
args = parser.parse_args()

if args.func == "checknfo":
    check_nfo()
elif args.func == "omdbsearch":
    omdb_update()
elif args.func == "omdbforce":
    if not args.show_s:
        pr.error("please supply show name with --s / -s")
    elif not db.exists(args.show_s):
        pr.error("invalid show: {}".format(args.show_s))
    else:
        omdb_force_update(args.show_s)
else:
    pr.error("wrong command: {}".format(args.func))
