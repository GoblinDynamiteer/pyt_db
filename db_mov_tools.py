# -*- coding: utf-8 -*-
import paths, json, os
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

def nfo_imdb_from_omdb_data(mov):
    imdbid_omdb = db.omdb_data(mov,'imdbID')
    let = db.movie_data(mov,'letter')
    path = os.path.join(mov_root, let, mov)
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
    if 'Error' in omdb_data:
        print_log("OMDb not found: {}".format(mov), category="warning")
    return False

def db_maintainance():
    need_save = False
    for mov in mlist:
        if not db.movie_data(mov, 'nfo'):
            if nfo_imdb_from_omdb_data(mov):
                print("Added nfo for {}".format(mov))
                need_save = True
            else:
                print_log("Could not add nfo for {}".format(mov), category="error")

        data = db.movie_data(mov, 'omdb')
        if not data or 'Error' in data:
            if update_omdb_search(mov):
                print("added omdb for {}".format(mov))
                need_save = True
            else:
                print_log("could not add omdb for {}".format(mov), category="error")

    if need_save:
        db.save()
    else:
        print_log("nothing updated")
