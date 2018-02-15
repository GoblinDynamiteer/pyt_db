import os

dummy_location = "C:\\Temp\MOVIE_DUMMY\\" # Fix for linux
last_folder_created = ""

def create_dummy_file(name, path):
    full_path = path + "\\" + name
    if not os.path.isfile(full_path):
        with open(full_path, 'w') as newfile:
            newfile.write("dummy")

print("Creating dummy files in " + dummy_location)
count = 0

with open("mov_dummy_filenames.txt", "r") as file_list:
    for line in file_list:
        line = line.replace("\r","")
        line = line.replace("\n","")
        lp = line.split("/");
        letter = lp[0]
        folder = lp[1]
        full_path = dummy_location + letter + "\\" + folder
        file_name = lp[2]

        if folder is not last_folder_created:
            last_folder_created = folder
            if not os.path.exists(full_path):
                os.makedirs(full_path)

        create_dummy_file(file_name, full_path)
