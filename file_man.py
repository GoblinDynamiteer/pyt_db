import platform
from os import path, stat
from datetime import datetime

def get_date(path_to_file_or_folder, convert=False):
    if platform.system() == 'Windows':
        ret_time = path.getctime(path_to_file_or_folder)
    else:
        ret_time = stat(path_to_file_or_folder)
        try:
            ret_time = stat.st_birthtime
        except:
            ret_time = stat.st_mtime
    return ret_time if convert is False else datetime.fromtimestamp(ret_time)
