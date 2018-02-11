from os import listdir, path
import re #regex
import sys

def get_file(movie, file_ext, full_path = False):
    path = gen_full_path(movie)
    for file in listdir(path):
        if file.endswith("." + file_ext):
            return path + str(file) if full_path else str(file)
    return None

def get_vid(movie):
    for ext in [ "mkv", "avi", "mp4" ]:
        vid = get_file(movie, ext)
        if vid:
            return vid
    return None

def print_no_line(string):
    print(string, end='')

def check_sub(movie, lang):
    return get_file(movie, lang + ".srt")

def gen_full_path(movie):
    return movies_location + movie['letter'] + "\\" + movie['folder'] + "\\"

def nfo_to_imdb(movie):
    f = open(get_file(movie, "nfo", full_path = True), "r")
    imdb_url = f.readline()
    f.close()
    re_imdb = re.compile("tt\d{1,}")
    imdb_id = re_imdb.search(imdb_url)
    return imdb_id.group(0) if imdb_id else False

movies_location = "M:\\"

# Empty dictionary
database = {}

movie_letter_dirs = listdir(movies_location)
movie_letter_dirs.sort()

for movie_letter in movie_letter_dirs:
    #if movie_letter is 'A':
    #    break
    movies = listdir(movies_location + movie_letter)
    movies.sort()
    for movie in movies:
        # FIXME: Clear line (string lenght fill with spaces? Raggarlosning)
        print("Checking " + movie_letter + " [" + movie + "]", end='\r')
        database[movie] = { 'letter' : movie_letter, 'folder' : movie }
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
            database[movie]['nfo'] = False
        # Check available srt-files
        database[movie]['subs'] = { 'sv' : check_sub(database[movie], "sv"), 'en' : check_sub(database[movie], "en") }
        # Check video filename
        vid = get_vid(database[movie])
        if vid is None:
            print("Could not determine video file for " + movie + "!")
        database[movie]['video'] = vid

print(database)
