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
        2014/7/14 
"""
from flask import Flask, Response



# Create Flask application
app = Flask(__name__)

@app.route('/')
def index():
	return "It works."

# @app.route('/download/<city_name>', methods=['GET'])
# def download(city_name):
# 	return 'you chosen %s' % city_name

@app.route('/taipei', methods = ['GET'])
def json():
	with open('Geoparks.json', 'rb') as json_file:
		json_data = json_file.read()
	
	resp = Response(json_data, status=200, mimetype='application/json')

	return resp

@app.route('/yokohama', methods = ['GET'])
def json():
	with open('Geoparks.json', 'rb') as json_file:
		json_data = json_file.read()
	
	resp = Response(json_data, status=200, mimetype='application/json')

	return resp

if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0')
