#-*- coding: utf-8 -*-
'''
    Copyright (c) 2014  OpenISDM

    Project Name:

        OpenISDM MAD-IS

    Version:

        1.0

    File Name:

        interfaceServer.py

    Abstract:

        interfaceServer.py is a module of Interface Server (IS) of
        Mobile Assistance for Disasters (MAD) in the OpenISDM
        Virtual Repository project.
        It create admin interface, database, and activate the server.

    Authors:

        Bai Shan-Wei, k0969032@gmail.com

    License:

        GPL 3.0 This file is subject to the terms and conditions defined
        in file 'COPYING.txt', which is part of this source code package.

    Major Revision History:

        2014/5/1: complete version 1.0
'''


from flask import Flask, url_for, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from wtforms import form, fields, validators
from flask.ext import admin, login
from flask_admin.contrib import sqla
from flask_admin import helpers, expose
from flask import jsonify
from configobj import ConfigObj
from threading import Thread
from communicate import demand

import os
import json2rdf
import xml.etree.ElementTree as ET
import requests
import socket

# Create Flask application
app = Flask(__name__)

#app.register_blueprint(action)
app.register_blueprint(demand)

db = SQLAlchemy(app)


show_menu = False;
# Create user model. For simplicity, it will store passwords in plain text.








if __name__ == '__main__':
    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()

    # Start app
    app.run(host= socket.gethostbyname(socket.gethostname()), port=int("80"), debug=True)
    #app.run(host= socket.gethostbyname(socket.gethostname()), port=int("80"))


