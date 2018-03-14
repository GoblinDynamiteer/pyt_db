# -*- coding: utf-8 -*-
import paths
import filetools as ftool
import movie as mtool
import db_mov
from printout import print_blue, print_no_line, print_color_between

import os
import datetime

db = db_mov.database()
if not db.load_success():
    quit()

mov_root = mtool.root_path()
letters = os.listdir(mov_root)
letters.sort()
new_count = 0

_valid_letters = { "#", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K",
    "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "VW", "X", "Y", "Z" }

def new_movie(letter, movie):
    fp = os.path.join(mov_root, letter, movie)
    mov = { 'letter' : letter, 'folder' : movie }
    date = ftool.get_creation_date(fp, convert=True)
    mov['date_created'] = date.strftime("%d %b %Y") if date is not None else None
    mov['date_scanned'] = datetime.datetime.now().strftime("%d %b %Y")
    mov['nfo'] = mtool.has_nfo(fp)
    mov['imdb'] = mtool.nfo_to_imdb(fp)
    mov['subs'] = {
        'sv' : mtool.has_subtitle(fp, "sv"),
        'en' : mtool.has_subtitle(fp, "en") }
    mov['video'] = mtool.get_vid_file(fp)
    mov['omdb'] = mtool.omdb_search(mov)
    print_color_between("Added [ {} ] to database!".format(movie), "blue")
    db.add(mov)

for letter in letters:
    if letter in _valid_letters:
        print("Scanning {}".format(letter))
        movies = os.listdir(os.path.join(mov_root, letter))
        movies.sort()
        for movie in movies:
            if movie.startswith("@"): # Diskstation
                continue;
            if not db.exists(movie):
                new_movie(letter, movie)
                new_count += 1
    else:
        continue

print("Done scanning. Found ({}) new movies.".format(new_count))
db.save()
