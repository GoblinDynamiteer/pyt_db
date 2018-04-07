# -*- coding: utf-8 -*-
import paths, json, os, argparse
import db_mov as movie_database
import filetools as ftool
import movie as mtool
from printout import print_class as pr

pr = pr(os.path.basename(__file__))
db = movie_database.database()
if not db.load_success():
    pr.error("database read error, quitting...")
    quit()

mov_root = mtool.root_path()
mlist = db.list_movies()
letters = os.listdir(mov_root)
letters.sort()

_valid_letters = { "#", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K",
    "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "VW", "X", "Y", "Z" }

def try_add_nfo(mov):
    imdbid_omdb = db.omdb_data(mov,'imdbID')
    let = db.movie_data(mov,'letter')
    path = os.path.join(mov_root, let, mov)
    if mtool.has_nfo(path): # user probabl manually added nfo
        imdb_id = mtool.nfo_to_imdb(path)
        db.update(mov, 'nfo', True)
        db.update(mov, 'imdb', imdb_id)
        return True
    if not imdbid_omdb:
        pr.warning("no imdb omdb-data for {}".format(mov))
        return False
    if imdbid_omdb and ftool.create_nfo(path, imdbid_omdb, "movie"):
        db.update(mov, 'nfo', True)
        return True
    return False

def update_omdb_search(mov):
    movie_data = db.movie_data(mov)
    omdb_data = mtool.omdb_search(movie_data)
    if omdb_data and 'Error' not in omdb_data:
        db.update(mov, 'omdb', omdb_data)
        return True
    if omdb_data and'Error' in omdb_data:
        pr.warning("OMDb not found: {}".format(mov))
    if not omdb_data:
        pr.warning("OMDb search returned None!: {}".format(mov))
    return False

def scan_for_deleted_movies():
    pr.info("scanning for deleted movies...")
    need_save = False
    for mov in mlist:
        if db.movie_data(mov, 'status') == "deleted":
            continue
        path_to_check = os.path.join(mov_root, db.movie_data(mov, 'letter'),
            db.movie_data(mov, 'folder'))
        if not os.path.isdir(path_to_check):
            pr.info("folder deleted: {}".format(path_to_check))
            db.update(mov, 'status', "deleted")
            need_save = True
    if need_save:
        db.save()
        ftool.copy_dbs_to_webserver("movie")
    else:
        pr.info("nothing updated")

def db_maintainance():
    pr.info("running moviedb maintainance...")
    need_save = False
    for mov in mlist:
        if db.movie_data(mov, 'status') == "deleted":
            continue
        if not db.movie_data(mov, 'status'):
            path_to_check = os.path.join(mov_root, db.movie_data(mov, 'letter'),
                db.movie_data(mov, 'folder'))
            if os.path.isdir(path_to_check):
                db.update(mov, 'status', "ok")
                need_save = True
        if not db.movie_data(mov, 'nfo') or not db.movie_data(mov, 'imdb'):
            if try_add_nfo(mov):
                pr.info("added nfo/imdb for {}".format(mov))
                need_save = True
            else:
                pr.error("could not add nfo for {}".format(mov))
        data = db.movie_data(mov, 'omdb')
        if not data or 'Error' in data:
            if update_omdb_search(mov):
                pr.info("added omdb for {}".format(mov))
                need_save = True
            else:
                pr.error("could not add omdb for {}".format(mov))
        elif "Title" in data and data['Title'].startswith("#"):
            pr.warning(f"{mov} has faulty title: [{data['Title']}]")
            pr.info("trying omdb rescan")
            if update_omdb_search(mov):
                if "Title" in data and data['Title'].startswith("#"):
                    pr.warning(f"failed, title is still [{data['Title']}]")
                else:
                    pr.info(f"added new omdb for {mov}")
                need_save = True
    if need_save:
        db.save()
        ftool.copy_dbs_to_webserver("movie")
    else:
        pr.info("nothing updated")

parser = argparse.ArgumentParser(description='MovieDb tools')
parser.add_argument('func', type=str, help='MovieDb command: maintain, checkdeleted')
args = parser.parse_args()

if args.func == "maintain":
    db_maintainance()
elif args.func == "checkdeleted":
    scan_for_deleted_movies()
else:
    pr.error("wrong command: {}".format(args.func))
