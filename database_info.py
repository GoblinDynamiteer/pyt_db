# -*- coding: utf-8 -*-
import json

#movies_location = "M:\\" # Fix for linux
movies_location = "C:\\Temp\MOVIE_DUMMY\\" # Dummy files
db_file = "db.json"
f = open("omdb_api.txt", "r")
omdb_api = f.readline()
f.close()

with open(db_file, 'r') as db:
    database = json.load(db)

movlist = []
# Test output

for movie in database:
    if database[movie]['subs']['sv'] is None:
        movlist.append(database[movie])

print("Missing sv.srt: ", end='')
print(len(movlist), end='')
print(" of ", end='')
print(len(database))
