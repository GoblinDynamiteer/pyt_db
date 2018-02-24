import platform
import os
from datetime import datetime

# Try to determine creation date of folder
def get_date(path_to_file_or_folder, convert=False):
    ret_time = os.path.getctime(path_to_file_or_folder)
    return ret_time if convert is False else datetime.fromtimestamp(ret_time)

# Create nfo file with IMDb-id for movie
def create_nfo(full_path, imdb):
    if not os.path.isfile(full_path):
        with open(full_path + "movie.nfo", 'w') as newfile:
            newfile.write(imdb)
