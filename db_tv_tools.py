# -*- coding: utf-8 -*-
import paths, json, os, argparse
import db_tv as tv_database
import filetools as ftool
import tvshow as tvtool
from printout import print_class as pr

pr = pr(os.path.basename(__file__))
db = tv_database.database()
if not db.load_success():
    pr.error("database read error, quitting...")
    quit()

tv_root = tvtool.root_path()
shows = os.listdir(tv_root)
shows.sort()

def check_nfo():
    for show in shows:
        if show.startswith("@"): # Diskstation
            continue;
        if tvtool.has_nfo(show):
            if tvtool.nfo_to_imdb(show):
                pr.info("{} has tvshow.nfo".format(show))
            else:
                pr.warning("{} has non-imdb tvshow.nfo".format(show))
                tvtool.add_nfo_manual(show, replace=True)
        else:
            tvtool.add_nfo_manual(show)

parser = argparse.ArgumentParser(description='TVDb tools')
parser.add_argument('func', type=str,
    help='TVDb command: maintain, checkdeleted, checknfo')
args = parser.parse_args()

if args.func == "checknfo":
    check_nfo()
elif args.func == "checkdeleted":
    # FIXME
    pr.warning("checkdeleted not implemented")
else:
    pr.error("wrong command: {}".format(args.func))
