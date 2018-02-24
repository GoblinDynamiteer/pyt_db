# -*- coding: utf-8 -*-
import json

class database:
    def __init__(self):
        self._db_file = "db.json"
        self._loaded_db = []
        self._load_db()
        self._mov_list = []
        self._key_list = []
        if self._loaded_db is not None:
            for mov in self._loaded_db.keys():
                self._mov_list.append(mov)
            for key in self._loaded_db[self._mov_list[0]].keys():
                self._key_list.append(key)

    # Load JSON database to variable
    def _load_db(self):
        try:
            with open(self._db_file, 'r') as db:
                self._loaded_db = json.load(db)
        except:
            print("Could not open file: {0}".format(self._db_file))
            self._loaded_db = None

    # Check if database loaded correctly
    def load_success(self):
        return True if self._loaded_db is not None else False

    # Get count of movies
    def count(self):
        return len(self._loaded_db)

    # Get a list of all movie titles as strings
    def list_movies(self):
        return self._mov_list

    # Get movie data
    def movie_data(self, movie, key=None):
        if isinstance(movie, list):
            movie = movie[0]
        try:
            if key is None:
                return self._loaded_db[movie]
            else:
                return self._loaded_db[movie][key]
        except:
            return None

    # Check if movie exists in loaded database
    def exists(self, movie_name):
        return True if movie_name in self._loaded_db else False

    # Get omdb data for movie
    def omdb_data(self, movie, key=None):
        omdb = self.movie_data(movie, key="omdb")
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

    # Search for movie titles, get hits as a list of strings
    def search(self, search_string, first_hit=False):
        res = []
        for movie_name in self._mov_list:
            if movie_name.lower().find(search_string.lower()) is not -1:
                res.append(movie_name)
                if first_hit is True:
                    break
        return res
