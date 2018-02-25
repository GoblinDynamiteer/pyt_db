# -*- coding: utf-8 -*-
import paths
from os import listdir, path
import re #regex
import sys
import filetools as ftool
import json
import pprint
from pathlib import Path
import platform
import movie as mtool
import os
import datetime
import db_mov

# Make it work for Python 2+3 and with Unicode
import io
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

# Print w/o new line
def print_no_line(string):
    print(string, end='')

db = db_mov.database()
if not db.load_success():
    quit()

movies_location = mtool.root_path()
mletter_dirs = listdir(movies_location)
mletter_dirs.sort()

for mletter in mletter_dirs:
    movies = listdir(os.path.join(movies_location, mletter))
    movies.sort()

    for movie in movies:
        fp = os.path.join(movies_location, mletter, movie)
        mov = { 'letter' : mletter, 'folder' : movie }
        date = ftool.get_creation_date(fp, convert=True)
        mov['date_created'] = date.strftime("%d %b %Y") if date is not None else None
        mov['date_scanned'] = datetime.datetime.now().strftime("%d %b %Y")
        mov['nfo'] = mtool.has_nfo(fp)
        mov['imdb'] = mtool.nfo_to_imdb(fp)
        mov['subs'] = { 'sv' : mtool.has_subtitle(fp, "sv"), 'en' : mtool.has_subtitle(fp, "en") }
        mov['video'] = mtool.get_vid_file(fp)
        mov['omdb'] = mtool.omdb_search(mov)
        db.add(mov)

db.save()
