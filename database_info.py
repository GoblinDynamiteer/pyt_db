# -*- coding: utf-8 -*-
import json
import db_mov as movie_database

db = movie_database.database()

if not db.load_success():
    print("Database read error, quitting...")
    quit()

print(db.count())
print(db.list_movies())
print()
print(db.search("american"))
print()
pie = db.search("american.pie", first_hit=True)
print(pie[0])
print(db.list_keys())

pie_data = db.movie_data(pie)
pie_data_omdb = db.omdb_data(pie)

print(pie_data_omdb)
