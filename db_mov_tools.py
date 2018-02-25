# -*- coding: utf-8 -*-
import paths, json, os
import db_mov as movie_database
import filetools as ftool
import movie as mtool
from printout import print_error, print_warning

db = movie_database.database()
if not db.load_success():
    print("Database read error, quitting...")
    quit()

mov_root = mtool.root_path()
mlist = db.list_movies()

def nfo_imdb_from_omdb_data(mov):
    imdbid_omdb = db.omdb_data(mov,'imdbID')
    let = db.movie_data(mov,'letter')
    path = os.path.join(mov_root, let, mov)
    if not imdbid_omdb:
        print_warning("No imdb omdb-data for {}".format(mov))
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
        print_warning("OMDb not found: {}".format(mov))
    return False

def db_maintainance():
    need_save = False
    for mov in mlist:
        if not db.movie_data(mov, 'nfo'):
            if nfo_imdb_from_omdb_data(mov):
                print("Added nfo for {}".format(mov))
                need_save = True
            else:
                print_error("Could not add nfo for {}".format(mov))

        data = db.movie_data(mov, 'omdb')
        if not data or 'Error' in data:
            if update_omdb_search(mov):
                print("Added omdb for {}".format(mov))
                need_save = True
            else:
                print_error("Could not add omdb for {}".format(mov))

    if need_save:
        db.save()
    else:
        print("db_maintainance: Nothing updated")
