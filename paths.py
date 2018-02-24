import sys, os

home = os.getenv("HOME")
p = os.path.join(home, "code", "omdb-search")

sys.path.append(p)
