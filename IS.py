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

    filename = city_name + '.json'
    with open(os.path.join(APP_JSONFILES, filename), 'rb') as json_file:
		json_data = json_file.read().decode('utf-8')

    resp = Response(json_data)
    resp.headers['Content-type'] = 'application/json; charset=utf-8'

    return resp

@app.route('/cities', methods=['GET'])
def lookup_citylist():

    citylist = []

    for (dirpath, dirnames, filenames) in walk(APP_JSONFILES):
        for count in filenames:
            rec = re.findall("^[A-Z][a-z|A-Z]+[^_]", count)
            citylist.extend(rec) 

    print citylist

    return jsonify(results=citylist)



if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0')
