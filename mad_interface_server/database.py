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

import sys
from flask_sqlalchemy import SQLAlchemy
# from wtforms import form, fields, validators
from mad_interface_server import app
db = SQLAlchemy(app)

'''from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'],
                       convert_unicode=True,
                       **app.config['DATABASE_CONNECT_OPTIONS'])
db = scoped_session(sessionmaker(autocommit=False,
                                 autoflush=False,
                                 bind=engine))

Model = declarative_base(name='Model')
Model.query = db.query_property()'''

def build_sample_db():
    """
        Populate a db with some entries.
    """

    import string

    db.drop_all()
    db.create_all()
    test_user = User(login="test", password="test",is_finish_setup=False)
    db.session.add(test_user)

    array = [
    ]

    for i in range(len(array)):
        user = User()
        pos = POS()
        fac = Facility()
        db.session.add(user)
        db.session.add(pos)
        db.session.add(fac)

    db.session.commit()
    return


class User(db.Model):

    '''
       Create user model. For simplicity, it will store passwords in plain text.
    '''
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(64))
    country = db.Column(db.String(32))
    location = db.Column(db.String(32))
    coordinates = db.Column(db.String(32))
    is_finish_setup = db.Column(db.Boolean, nullable=False)

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username

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


class POS(db.Model):

    '''
       Create POS model.
    '''
    number = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(100))
    city = db.Column(db.String(32))
    district = db.Column(db.String(64))
    partition_method = db.Column(db.Unicode(64))
    bound_min_point = db.Column(db.Unicode(64))
    bound_max_point = db.Column(db.Unicode(64))
    latitude = db.Column(db.Unicode(64))
    longitude = db.Column(db.Unicode(64))
    topic_dir = db.Column(db.Unicode(128))
    callback_url = db.Column(db.Unicode(128))
    is_subscribe = db.Column(db.Boolean, nullable=False)

    def __unicode__(self):
        return self.name


class Facility(db.Model):
    '''
       Create facility model.
    '''
    number = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(100))
    name = db.Column(db.Unicode(64))
    city = db.Column(db.Unicode(32))
    type = db.Column(db.Unicode(32))
    category = db.Column(db.Unicode(64))
    district = db.Column(db.Unicode(64))
    address = db.Column(db.Unicode(128))
    telephone = db.Column(db.Unicode(64))
    latitude = db.Column(db.Unicode(64))
    longitude = db.Column(db.Unicode(64))
    description = db.Column(db.Unicode(255))

    def __unicode__(self):
        return self.name