# -*- coding: utf-8 -*-
import paths, os, platform, re, omdb
from printout import print_warning, print_no_line, print_blue, print_success, print_error, print_color_between

_mov_letters = { '#', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', \
    'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'VW', 'X', 'Y', 'Z' }

# Check if path is a valid movie root dir
def valid_movie_path(path):
    for let in _mov_letters:
        p = os.path.join(path, let)
        if not os.path.exists(p):
            return False
    return True

# Determine movie root path
def root_path():
    path = ""
    if platform.system() == 'Linux':
        path = str(os.getenv("HOME")) + "/smb/film"
    if platform.system() == 'Windows':
        path = "M:"
    if not valid_movie_path(path):
        print("Could not find movies root location!")
        quit()
    return path

# Check if movie has srt file
def has_subtitle(path, lang):
    return _get_file(path, lang + ".srt")

# Check if movie has srt file
def has_nfo(path):
    return True if _get_file(path, "nfo") is not None else False

# Extract IMDb-id from nfo
def nfo_to_imdb(path):
    if not has_nfo(path):
        return None
    f = open(_get_file(path, "nfo", full_path = True), "r")
    imdb_url = f.readline()
    f.close()
    re_imdb = re.compile("tt\d{1,}")
    imdb_id = re_imdb.search(imdb_url)
    return imdb_id.group(0) if imdb_id else None

# Determine video file for movie
def get_vid_file(path):
    for ext in [ "mkv", "avi", "mp4" ]:
        vid = _get_file(path, ext)
        if vid:
            return vid
    return None

# Get files for movie
def _get_file(path, file_ext, full_path = False):
    if not os.path.exists(path):
        print("_get_file: {} does not exist!".format(path))
        return None
    for file in os.listdir(path):
        if file.endswith("." + file_ext):
            return os.path.join(path, str(file)) if full_path else str(file)
    return None

# Determine letter from movie folder
def determine_letter(folder):
    let = folder[0:1]
    for prefix in ['The.', 'An.', 'A.']:
        if folder.startswith(prefix):
            let = folder[len(prefix):len(prefix) + 1]
    if let is "V" or let is "W":
        return "VW"
    return let

# Try to determine movie title from folder name
def determine_title(folder, replace_dots_with=' '):
    re_title = re.compile(".+?(?=\.(\d{4}|REPACK|720p|1080p|DVD|BluRay))")
    title = re_title.search(folder)
    if title is not None:
        title = re.sub('(REPACK|LiMiTED|EXTENDED|Unrated)', '.', title.group(0))
        title = re.sub('\.', replace_dots_with, title)
        return title
    else:
        print("determine_title: Could not get title for: " + folder)
        return None

# Try to determine movie year from folder name
def determine_year(folder):
    re_year = re.compile("(19|20)\d{2}")
    year = re_year.search(folder)
    if year is not None:
        return year.group(0)
    else:
        print("determine_year: Could not get year for: " + folder)
        return None

# Search OMDb for movie
def omdb_search(movie):
    folder = movie['folder']
    print_color_between("Searching OMDb for [ {} ] ".format(folder),
        "blue", endl=False)
    if movie['imdb'] is not None:
        print_no_line("Using IMDb-id: ")
        omdb_search = omdb.omdb_search(search_string = str(movie['imdb']), \
            search_type=None, search_year=None)
    else:
        print_no_line("Using Title : ")
        title = determine_title(folder , replace_dots_with='+')
        year =  determine_year(folder )
        omdb_search = omdb.omdb_search(search_string = title, \
            search_type="movie", search_year=year)
    data = omdb_search.data()
    try:
        if data['Response'] is "False":
            print_warning("Not found!")
            return None
        print_success("Got data!")
        return data
    except:
        print_error("Error!")
        return None
