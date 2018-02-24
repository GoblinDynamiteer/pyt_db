# -*- coding: utf-8 -*-
from os import listdir, path
import re #regex
import sys
import file_man
import omdb
import json
import pprint
from pathlib import Path
import platform
import movie
import os

# Make it work for Python 2+3 and with Unicode
import io
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

# Get files for movie
def get_file(movie, file_ext, full_path = False):
    path = gen_full_path(movie)
    for file in listdir(path):
        if file.endswith("." + file_ext):
            return os.path.join(path, str(file)) if full_path else str(file)
    return None

# Determine video file for movie
def get_vid(movie):
    for ext in [ "mkv", "avi", "mp4" ]:
        vid = get_file(movie, ext)
        if vid:
            return vid
    return None

# Search OMDb for movie
def omdb_search(movie):
    print_no_line("Searching OMDb for [ {} ] ".format(movie['folder']))
    if movie['imdb'] is not None:
        print_no_line("Using IMDb-id: ")
        omdb_search = omdb.omdb_search(search_string = str(movie['imdb']), \
            api_key=omdb_api, search_type=None, search_year=None)
    else:
        print_no_line("Using Title : ", endl='')
        title = title_from_folder(movie, replace_dots_with='+')
        year = year_from_folder(movie)
        omdb_search = omdb.omdb_search(search_string = title, \
            api_key=omdb_api, search_type="movie", search_year=year)
    data = omdb_search.data()
    try:
        if data['Response'] is "False":
            print("Not found!")
            return None
        print("Got data!")
        return omdb_search.get_json()
    except:
        return None

# Try to determine movie title from folder name
def title_from_folder(movie, replace_dots_with=' '):
    re_title = re.compile(".+?(?=\.(\d{4}|REPACK|720p|1080p|DVD|BluRay))")
    title = re_title.search(movie['folder'])
    if title is not None:
        title = re.sub('(REPACK|LiMiTED|EXTENDED|Unrated)', '.', title.group(0))
        title = re.sub('\.', replace_dots_with, title)
        return title
    else:
        print("title_from_folder: Could not get title for: " + movie['folder'])
        return None

# Try to determine movie year from folder name
def year_from_folder(movie):
    re_year = re.compile("(19|20)\d{2}")
    year = re_year.search(movie['folder'])
    if year is not None:
        return year.group(0)
    else:
        print("year_from_folder: Could not get year for: " + movie['folder'])
        return None

# Print w/o new line
def print_no_line(string):
    print(string, end='')

# Check if movie has srt file
def check_sub(movie, lang):
    return get_file(movie, lang + ".srt")

# Generate full path to movie
def gen_full_path(movie):
    return os.path.join(movies_location, movie['letter'],  movie['folder'])

# Extract IMDb-id from nfo
def nfo_to_imdb(movie):
    f = open(get_file(movie, "nfo", full_path = True), "r")
    imdb_url = f.readline()
    f.close()
    re_imdb = re.compile("tt\d{1,}")
    imdb_id = re_imdb.search(imdb_url)
    return imdb_id.group(0) if imdb_id else False


movies_location = ""
if platform.system() == 'Linux':
    movies_location = str(Path.home()) + "/smb/film"
if platform.system() == 'Windows':
    movies_location = "M:"

if not movie.valid_movie_path(movies_location):
    print("Could not set movies location!")
    quit()

db_file = "db.json"
f = open("omdb_api.txt", "r")
omdb_api = f.readline()
f.close()

# Empty dictionary
database = {}

movie_letter_dirs = listdir(movies_location)
movie_letter_dirs.sort()

for movie_letter in movie_letter_dirs:
    movies = listdir(os.path.join(movies_location, movie_letter))
    movies.sort()

    if movie_letter == 'B':
        break

    for movie in movies:
        # FIXME: Clear line (string lenght fill with spaces? Raggarlosning)
        #print("Checking " + movie_letter + " [" + movie + "]", end='\r')
        database[movie] = { 'letter' : movie_letter, 'folder' : movie }
        #continue

        # Get folder creation datetime
        cdate = file_man.get_date(gen_full_path(database[movie]), convert=True)
        # Remove microseconds, convert to format '13 Jan 2017' to match OMDb response
        database[movie]['created'] = cdate.replace(microsecond=0).strftime("%d %b %Y")
        # Check if movie folder has nfo-file
        if get_file(database[movie], "nfo"):
            database[movie]['nfo'] = True
            imdb_id = (nfo_to_imdb(database[movie]))
            if imdb_id:
                database[movie]['imdb'] = imdb_id
            else:
                print("Faulty nfo for:" + movie + "!")
                database[movie]['imdb'] = None
        else:
            print("Missing nfo for:" + movie + "!")
            database[movie]['nfo'] = False
            database[movie]['imdb'] = None
        # Check available srt-files
        database[movie]['subs'] = { 'sv' : check_sub(database[movie], "sv"), 'en' : check_sub(database[movie], "en") }
        # Check video filename
        vid = get_vid(database[movie])
        if vid is None:
            print("Could not determine video file for " + movie + "!")
        database[movie]['video'] = vid
        database[movie]['omdb'] = omdb_search(database[movie])

        # Set imdb to data from omdb search, if available
        if database[movie]['imdb'] is None and database[movie]['omdb'] is not None:
            print("Found id from omdb-search: ")
            imdb_id = database[movie]['omdb']["imdbID"]
            print(imdb_id)
            database[movie]['imdb'] = imdb_id
            file_man.create_nfo(gen_full_path(database[movie]), imdb_id)

with open(db_file, 'w', encoding='utf8') as outfile:
    str_ = json.dumps(database,
        indent=4, sort_keys=True,
        separators=(',', ': '), ensure_ascii=False)
    outfile.write(to_unicode(str_))

#for movie in database:
    #for omdb_data in database[movie]['omdb']:
    #    print(omdb_data + ": " + str(database[movie]['omdb'][omdb_data]))
