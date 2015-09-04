# -*- coding: utf-8 -*-
"""
Copyright (c) 2014  OpenISDM

    Project Name:

        OpenISDM MAD-IS

    Version:

        0.01

    File Name:

        is.py

    Abstract:

        is.py is a module of Interface Server (IS) of
        Mobile Assistance for Disasters (MAD) in the OpenISDM
        Virtual Repository project.
        It create admin interface, database, and activate the server.

    Authors:

        Johnson Su, johnsonsu@iis.sinica.edu.tw

    License:

        GPL 3.0 This file is subject to the terms and conditions defined
        in file 'COPYING.txt', which is part of this source code package.

    Major Revision History:
        2015/7/14
        2015/9/1 
"""
import os
from os import walk

from json import load, JSONEncoder

import re

from flask import Flask, Response, jsonify

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_JSONFILES = os.path.join(APP_ROOT, 'Geojsonfiles')

# Create Flask application
app = Flask(__name__)

@app.route('/')
def index():
	return "It works."


@app.route('/datasets/<city_name>', methods=['GET'])
def get_datasets(city_name):

    stringUpper = city_name.upper()
    
    json_data = ""
    
    regex = re.compile(r"^" + stringUpper + r".+", re.IGNORECASE)

    outjson = dict(features=[], type='FeatureCollection')

    for (dirpath, dirnames, filenames) in walk(APP_JSONFILES):
        for filename in filenames:
            if stringUpper in filename:
                result = regex.match(filename)
                if result is not None:
                    with open(os.path.join(APP_JSONFILES, result.group(0)), 'rb') as json_file:
                        outjson['features'] += merge_geojsons(json_file)

    return jsonify(outjson)


@app.route('/cities', methods=['GET'])
def lookup_citylist():

    city_list = []
    abbr_number = 3

    for (dirpath, dirnames, filenames) in walk(APP_JSONFILES):
        for filename in filenames:
            list_result = re.findall("^[A-Z][A-Z]*[^_]", filename)
            string_result = "".join(list_result).lower()
            if string_result is not "":
                if len(string_result) >= abbr_number:
                    city_list.append(string_result.title()) 
                else:
                    city_list.append(string_result.upper())

    city_sets = list(set(city_list))

    return jsonify(results=city_sets)

def merge_geojsons(json_file):

    injson = load(json_file)

    if injson.get('type', None) != 'FeatureCollection':
        raise Exception('Sorry, "%s" does not look like GeoJSON' % infile)
                    
    if type(injson.get('features', None)) != list:
            raise Exception('Sorry, "%s" does not look like GeoJSON' % infile)

    return injson['features']


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
