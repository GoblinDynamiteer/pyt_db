# -*- coding: utf-8 -*-
import paths, json, io, os, filetools
import diskstation as ds
from config import configuration_manager as cfg
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

try:
    to_unicode = unicode
except NameError:
    to_unicode = str

class database:
    def __init__(self):
        self._config = cfg()
        self.script_path = os.path.dirname(os.path.realpath(__file__))
        self._db_file  = self._config.get_setting("path", "tvdb")
        self._loaded_db = None
        self._load_db()
        self._show_list = []
        self._key_list = []
        if self._loaded_db is not None and self._loaded_db:
            for show in self._loaded_db.keys():
                self._show_list.append(show)
            for key in self._loaded_db[self._show_list[0]].keys():
                self._key_list.append(key)

    # Load JSON database to variable
    def _load_db(self):
        if filetools.is_file_empty(self._db_file):
            self._loaded_db = {}
            print_log("creating empty database", category="warning")
        else:
            try:
                with open(self._db_file, 'r') as db:
                    self._loaded_db = json.load(db)
                    print_log("loaded database file: [ {} ]".format(self._db_file))
            except:
                print_log("Could not open file: {0}".format(self._db_file),
                    category="error")
                self._loaded_db = None

    # Save to database JSON file
    def save(self):
        with open(self._db_file, 'w', encoding='utf8') as outfile:
            str_ = json.dumps(self._loaded_db,
                indent=4, sort_keys=True,
                separators=(',', ': '), ensure_ascii=False)
            outfile.write(to_unicode(str_))
        print_log("saved database to {}!".format(self._db_file))
        if self.backup_to_ds():
            print_log("backed up database!")
        else:
            print_log("could not backup database!", category="warning")

    # Add show to database
    def add(self, show):
        if self.load_success():
            key = show['folder']
            if key is not None:
                self._loaded_db[key] = show

    def add_ep(show, season, episode):
        if self.load_success():
            self._loaded_db[show]['seasons'][season].append(episode)

    # Check if database loaded correctly
    def load_success(self):
        return True if self._loaded_db is not None else False

    # Update data for movie
    def update(self, show_folder, key, data):
        if not self.exists(show_folder):
            print_log("update: {} is not in database!".format(show_folder),
                category="warning")
        else:
            try:
                self._loaded_db[show_folder][key] = data
                if key is 'omdb':
                    data = "omdb-search"
                print_log("Updated {} : {} = {}".format(show_folder, key, data))
            except:
                print_log("update: Could not update {}!".format(show_folder),
                    category="warning")

    # Get count of movies
    def count(self):
        return len(self._loaded_db)

    # Get a list of all movie titles as strings
    def list_shows(self):
        return self._show_list

    # Get movie data
    def show_data(self, show, key=None):
        if isinstance(show, list):
            show = show[0]
        try:
            if key is None:
                return self._loaded_db[show]
            else:
                return self._loaded_db[show][key]
        except:
            return None

    def has_ep(self, show, season, ep):
        for season in self._loaded_db[show]['seasons']:
            for episode in season['episodes']:
                if episode['file'] == ep:
                    return True
        return False

    # Check if movie exists in loaded database
    def exists(self, show_name):
        return True if show_name in self._loaded_db else False

    # Backup database file
    def backup_to_ds(self):
        bpath = self._config.get_setting("path", "backup")
        dest = os.path.join(bpath, "Database", "TV")
        return filetools.backup_file(self._db_file, dest)

    # Get omdb data for show
    def omdb_data(self, show, key=None):
        omdb = self.movie_data(show, key="omdb")
        try:
            if key is None:
                return omdb
            else:
                return omdb[key]
        except:
            return None

    # Get a list of all key values as strings
    def list_keys(self):
        return self._key_list
