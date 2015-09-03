import os
from os import walk

import re

from json import load, JSONEncoder

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_JSONFILES = os.path.join(APP_ROOT, 'Geojsonfiles')


string = "taipei"
stringUpper = string.upper()
json_data = []

outjson = dict(type='FeatureCollection', features=[])

print r"^" + stringUpper + r".+"

regex=re.compile(r"^" + stringUpper + r".+", re.IGNORECASE)

for (dirpath, dirnames, filenames) in walk(APP_JSONFILES):
	for filename in filenames:
		if stringUpper in filename:
			result = regex.match(filename)
			if result is not None:
				with open(os.path.join(APP_JSONFILES, result.group(0)), 'rb') as json_file:
					injson = load(json_file)

					if injson.get('type', None) != 'FeatureCollection':
						raise Exception('Sorry, "%s" does not look like GeoJSON' % infile)
					
					if type(injson.get('features', None)) != list:
						raise Exception('Sorry, "%s" does not look like GeoJSON' % infile)

					outjson['features'] += injson['features']

	print outjson