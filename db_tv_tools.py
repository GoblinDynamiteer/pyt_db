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

def scan_for_deleted():
    pr.info("scanning for deleted epsisodes")
    save_db = False
    deleted_count = 0
    for show_s in db.list_shows():
        show_d = db.data(show_s)
        season_index = 0
        need_update = False
        for season_d in show_d["seasons"]:
            episode_index = 0
            for episode_d in season_d["episodes"]:
                if episode_d["status"] == "deleted":
                    continue
                file_path = os.path.join(tv_root, show_d["folder"], \
                    season_d["folder"], episode_d["file"])
                if not ftool.is_existing_file(file_path):
                    pr.info(f"found deleted episode: [{episode_d['file']}]")
                    deleted_count += 1
                    need_update = True
                    show_d["seasons"][season_index]["episodes"][episode_index] \
                        ["status"] = "deleted"
                episode_index += 1
            season_index += 1
        if need_update:
            save_db = True
            db.update(show_d["folder"], show_d, key=None)
    pr.info("done!")
    if deleted_count > 0:
        pr.info(f"found {deleted_count} deleted items")
    if save_db:
        db.save()

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
        need_update = False
        show_d = db.data(show_s)
        nfo_imdb = tvtool.nfo_to_imdb(show_d)
        if nfo_imdb:
            if show_d["imdb"] != nfo_imdb:
                show_d["imdb"] = nfo_imdb
                need_update = True
                pr.info(f"found new (hopefully) imdb-id [{nfo_imdb}] in nfo for {show_s}")
        if not show_d["omdb"]:
            omdb_result = tvtool.omdb_search_show(show_d)
            if omdb_result:
                show_d["omdb"] = omdb_result
                need_update = True
                success_count += 1
        season_index = 0
        for season_d in show_d["seasons"]:
            if not season_d["omdb"]:
                omdb_result = tvtool.omdb_search_season(show_d, season_d["folder"])
                if omdb_result:
                    show_d["seasons"][season_index]["omdb"] = omdb_result
                    need_update = True
                    success_count += 1
            episode_index = 0
            for episode_d in season_d["episodes"]:
                if episode_d["status"] == "deleted":
                    continue
                if not episode_d["omdb"]:
                    omdb_result = tvtool.omdb_search_episode(
                        show_d, season_d["folder"], episode_d["file"])
                    if omdb_result:
                        need_update = True
                        success_count += 1
                        show_d["seasons"][season_index]["episodes"][episode_index]["omdb"] = omdb_result
                episode_index += 1
            season_index +=1
        if need_update:
            save_db = True
            db.update(show_d["folder"], show_d, key=None)
    pr.info("done!")
    if success_count > 0:
        pr.info("successfully updated omdb-data for {} items".format(success_count))
    if save_db:
        db.save()

def scan_all_subtitles():
    pr.info("scanning for subs")
    save_db = False
    new_count = 0
    for show_s in db.list_shows():
        show_d = db.data(show_s)
        season_index = 0
        need_update = False
        for season_d in show_d["seasons"]:
            episode_index = 0
            for episode_d in season_d["episodes"]:
                if episode_d["status"] == "deleted":
                    continue
                if not "subs" in episode_d:
                    need_update = True
                    episode_d['subs'] = {
                        'sv' : tvtool.has_subtitle(show_d, episode_d["file"], "sv"),
                        'en' : tvtool.has_subtitle(show_d, episode_d["file"], "en") }
                    if episode_d['subs']['sv']:
                        pr.info(f"found [{episode_d['subs']['sv']}]")
                    if episode_d['subs']['en']:
                        pr.info(f"found [{episode_d['subs']['en']}]")
                else:
                    if not episode_d['subs']['sv']:
                        episode_d['subs']['sv'] = tvtool.has_subtitle(show_d, episode_d["file"], "sv")
                        if episode_d['subs']['sv']:
                            need_update = True
                            pr.info(f"found [{episode_d['subs']['sv']}]")
                    if not episode_d['subs']['en']:
                        episode_d['subs']['en'] = tvtool.has_subtitle(show_d, episode_d["file"], "en")
                        if episode_d['subs']['en']:
                            need_update = True
                            pr.info(f"found [{episode_d['subs']['en']}]")
            season_index += 1
        if need_update:
            save_db = True
            db.update(show_d["folder"], show_d, key=None)
    pr.info("done!")
    if save_db:
        db.save()

def omdb_force_update(show_s):
    success_count = 0
    pr.info("force-updating omdb-data for {}".format(show_s))
    show_d = db.data(show_s)
    nfo_imdb = tvtool.nfo_to_imdb(show_d)
    if nfo_imdb:
        if show_d["imdb"] != nfo_imdb:
            show_d["imdb"] = nfo_imdb
            need_update = True
            pr.info(f"found new (hopefully) imdb-id [{nfo_imdb}] in nfo for {show_s}")
    omdb_result = tvtool.omdb_search_show(show_d)
    show_d["omdb"] = omdb_result
    season_index = 0
    for season_d in show_d["seasons"]:
        omdb_result = tvtool.omdb_search_season(show_d, season_d["folder"])
        show_d["seasons"][season_index]["omdb"] = omdb_result
        episode_index = 0
        for episode_d in season_d["episodes"]:
            if episode_d["status"] == "deleted":
                continue
            omdb_result = tvtool.omdb_search_episode(show_d, season_d["folder"], episode_d["file"])
            show_d["seasons"][season_index]["episodes"][episode_index]["omdb"] = omdb_result
            episode_index += 1
        season_index +=1
    db.update(show_d["folder"], show_d, key=None)
    db.save()

parser = argparse.ArgumentParser(description='TVDb tools')
parser.add_argument('func', type=str,
    help='TVDb command: maintain, checkdeleted, checknfo, omdbsearch, omdbforce, subscan')
parser.add_argument('--show', "-s", type=str, dest="show_s", default=None, help='show to process')
args = parser.parse_args()

if args.func == "checknfo":
    check_nfo()
elif args.func == "subscan":
    scan_all_subtitles()
elif args.func == "checkdeleted":
    scan_for_deleted()
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
