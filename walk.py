from os import walk

import os


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_jsonfiles = os.path.join(APP_ROOT, 'Geojsonfiles')

f = []
for (dirpath, dirnames, filenames) in walk('venv'):
    f.extend(filenames)
    break
print f