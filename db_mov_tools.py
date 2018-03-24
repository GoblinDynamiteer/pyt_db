# -*- coding: utf-8 -*-
import paths, json, os, argparse
import db_mov as movie_database
import filetools as ftool
import movie as mtool
from printout import print_blue, print_no_line, print_color_between
from printout import print_script_name as psn
from printout import print_color_between as pcb
from printout import print_error, print_warning

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

db = movie_database.database()
if not db.load_success():
    print_log("database read error, quitting...", category="error")
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
        print_log("no imdb omdb-data for {}".format(mov), category="warning")
        return False
    if imdbid_omdb and ftool.create_nfo(path, imdbid_omdb):
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
        print_log("OMDb not found: {}".format(mov), category="warning")
    if not omdb_data:
        print_log("OMDb search returned None!: {}".format(mov),
            category="warning")
    return False

def scan_for_deleted_movies():
    print_log("scanning for deleted movies...")
    need_save = False
    for mov in mlist:
        if db.movie_data(mov, 'status') == "deleted":
            continue
        path_to_check = os.path.join(mov_root, db.movie_data(mov, 'letter'),
            db.movie_data(mov, 'folder'))
        if not os.path.isdir(path_to_check):
            print_log("folder deleted: {}".format(path_to_check))
            db.update(mov, 'status', "deleted")
            need_save = True
    if need_save:
        db.save()
        ftool.copy_dbs_to_webserver()
    else:
        print_log("nothing updated")

def db_maintainance():
    print_log("running moviedb maintainance...")
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
                print_log("added nfo/imdb for {}".format(mov))
                need_save = True
            else:
                print_log("could not add nfo for {}".format(mov), category="error")
        data = db.movie_data(mov, 'omdb')
        if not data or 'Error' in data:
            if update_omdb_search(mov):
                print_log("added omdb for {}".format(mov))
                need_save = True
            else:
                print_log("could not add omdb for {}".format(mov), category="error")

    if need_save:
        db.save()
        ftool.copy_dbs_to_webserver()
    else:
        print_log("nothing updated")

parser = argparse.ArgumentParser(description='MovieDb tools')
parser.add_argument('func', type=str, help='MovieDb command: maintain, checkdeleted')
args = parser.parse_args()

if args.func == "maintain":
    db_maintainance()
elif args.func == "checkdeleted":
    scan_for_deleted_movies()
else:
    print_log("wrong command: {}".format(args.func), category="error")
