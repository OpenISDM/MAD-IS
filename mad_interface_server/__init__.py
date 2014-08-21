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
import os

from flask import Flask, render_template
from flask import jsonify
from flask.ext import login

from mad_interface_server.communicate import demand

# Create Flask application
app = Flask(__name__)

# Loading config file 'isconfig'
app.config.from_object('isconfig')

# app.register_blueprint(action)
app.register_blueprint(demand)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

from mad_interface_server import database, account
# from mad_interface_server import account
# Build a sample db on the fly, if one does not exist yet.
if not os.path.exists(app.config['DATABASE_PATH']):
    database.build_sample_db()

# Initialize flask-login
account.init_login()
account.init_admin()