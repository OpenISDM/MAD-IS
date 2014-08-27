# -*- coding: utf-8 -*-
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

from mad_interface_server.database import db, User, POS, Facility
from flask.ext import login
from fileSystem import FileSystem
from configobj import ConfigObj
import xml.etree.ElementTree as ET
import os
import json2rdf


fs = FileSystem()


def answer(request):

    info = Information()

    jsonText = {'status': 'OK',
                'coordinates': info.coordinates,
                "cityLocation": info.location
                }

    data = ""

    if request == 'geoInfo':
        data = info.get_district('district', fs.mydir)
    elif request == 'exist_Country&City':
        data = fs.search_dir_file('/ConfigFile')
    elif request == 'setupInfo':
        data = info.get_facility_info()
        config_info = info.get_config(fs.mydir + '/ConfigFile')
        ward_info = info.get_district('district', fs.mydir)
        pos_info = info.get_pos_info()
        jsonText['configInfo'] = config_info
        jsonText['wardInfo'] = ward_info
        jsonText['posInfo'] = pos_info

    jsonText['data'] = data

    return jsonText

def build_info(data):
    info = Information()
    topic_path = '/static/Topic/'
    if data["purpose"] == 'setup':
        fs.create_folder('/ConfigFile/' + info.login)
        info.store_location(data["latLng"], data["location"])
        info.create_config(fs.mydir, data["key"])
        fs.create_xml_file(info.login, data["wardInfo"].encode('utf-8'))
        info.store_pos(data["location"], data["posArray"], fs.my_web_addr)
        info.finish_setup()
    elif data["purpose"] == 'facility':
        info.store_fac(info.location, data)
    elif data["purpose"] == 'update':
        sub_url = info.update_db(data)
        rdf_text = json2rdf.generate_rdf_text(data["textContent"])
        fs.download_file(topic_path, data["posName"], 'rdf', rdf_text, 'w')
        fs.download_file(            topic_path, data["posName"], 'png', data["imgUrl"], 'wb')
        # content_distribution(sub_url)
    elif data["purpose"] == 'download':
        fs.create_folder(topic_path+data["posName"])
        rdf_text = json2rdf.generate_rdf_text(data["textContent"])
        fs.download_file(topic_path, data["posName"], 'rdf', rdf_text, 'w')
        fs.download_file(            topic_path, data["posName"], 'png', data["imgUrl"], 'wb')


class Information:
    '''
        The class "information" allow you/me insert and extract data.
    '''

    def __init__(self):
        '''
            Initialize user and its city and country he/she serve
        '''
        self.user = User.query.filter_by(
            id=login.current_user.get_id()).first()
        self.login = self.user.login
        self.location = self.user.location
        self.coordinates = self.user.coordinates

    def store_location(self, coordinates, location):
        '''
            Store user's location when sending the registration form.
        '''
        self.user.location = location
        self.user.coordinates = coordinates
        db.session.commit()

    def finish_setup(self):
        '''
            Store user's location when sending the registration form.
        '''

        self.user.is_finish_setup = True
        db.session.commit()

    def get_config(self, configdir):
        '''
            Get configuration file's content

            configdir:
                configuration file's directory

            filename:
                configuration file's path

            Returned Value:
                If the function find the file, the returned is a json
                object of configuration content;
                otherwise, the returned value is null.
        '''
        filename = configdir + '/' + self.login + '/' + self.login + '.ini'
        if os.path.exists(filename):
            # if file is exist, get its content.
            config = ConfigObj(filename)
            config_info = {
                "wardpath": config['Country Info']['District Info Path'],
                "key": config['Boundary']['ApiKey']
            }
            return config_info
        else:
            # file is not exist, return null.
            return 'Null'

    def create_config(self, mydir, key):
        """
            Create the configuration file

            mydir:
                server's path

            coordinate :
                the original coordinate of city

            key:
                The cloud document ID

            Returned Value:
                If the function find the file, the returned is a json object
                of configuration content;                otherwise, the returned value is null.
        """

        config = ConfigObj()
        config.filename = mydir + '/ConfigFile/' + \
            self.login + '/' + self.login + '.ini'
        config['Country Info'] = {}
        config['Country Info']['District Info Path'] = mydir + \
            "/District Info/" + self.login + '.xml'
        config['Boundary'] = {}
        config['Boundary']['ApiKey'] = key
        config.write()

    def get_district(self, key, mydir):
        '''
            Get districts information of city

            key:
                The key word that can find information from the file

            mydir:
                server's path

            Returned Value:
                The returned is a json array of district information;
                otherwise, the returned value is null.
        '''

        if key == 'district':

            '''
                Start to parse xml file
            '''
            region_info = []
            tree = ET.parse(mydir + '/District Info/' + self.login + '.xml')
            root = tree.getroot()
            for info in root.findall('District'):
                data = {
                    "District": info.find("Name").text,
                    "Code": info.find("PostalCode").text
                }
                region_info.append(data)
            return region_info
        else:
            return 'Null'

    def store_db(self, content, server_location):
        '''
            Store information of POS servers and facilities

            content :
                data that will be inserted to database

            server_location:
                server's path
        '''

        if content[1] == 'posServer':

            # Store the information of POS server
            topic_path = server_location + '/static/Topic/' + content[3]
            pos = POS(id=content[3], city=self.location,
                      district=content[4].decode('utf8'),
                      partition_method='District',
                      latitude=content[5], longitude=content[6],
                      topic_dir=topic_path, is_subscribe=False)

            db.session.add(pos)

        elif content[1] == 'facility':

            # Store the information of facility

            facility = Facility(city=self.location, id=content[2],
                                name=content[3].decode('utf8'),
                                type=content[4].decode('utf8'),
                                district=content[5].decode('utf8'),
                                address=content[6].decode('utf8'),
                                telephone=content[7].decode('utf8'),
                                latitude=content[8].decode('utf8'),
                                longitude=content[9].decode('utf8'),
                                description=content[10].decode('utf8'),
                                category=content[11])

            db.session.add(facility)

        db.session.commit()

    def store_pos(self, city, content, server_location):

        for p in range(len(content)):

            topic_path = server_location + \
                '/static/Topic/' + content[p]["special_id"]

            pos = POS(id=content[p]["special_id"], city=city,
                      district=content[p]["ward"], partition_method='District',
                      latitude=content[p]["lat"], longitude=content[p]["lng"],
                      topic_dir=topic_path, is_subscribe=False)

            db.session.add(pos)
            db.session.commit()

    def store_fac(self, city, content):
        # for f in range(len(content)):

        facility = Facility(city=city, id=content["id"],
                            name=content["name"],
                            type=content["type"],
                            district=content["district"],
                            address=content["address"],
                            telephone=content["telephone"],
                            latitude=content["latitude"],
                            longitude=content["longitude"],
                            description=content["description"],
                            category=content["category"])

        db.session.add(facility)
        db.session.commit()

    def get_facility_info(self):
        '''
            Extract information of facilities servers

            Returned Value:
                The json array of facilities information
        '''

        all_fac = []
        # Start to query from Facility data table
        for f in db.session.query(Facility):
            if f.city == self.location:
                fac = {
                    'id': f.id,
                    'name': f.name,
                    'type': f.type,
                    'category': f.category,
                    'district': f.district,
                    'address': f.address,
                    'telephone': f.telephone,
                    'latitude': f.latitude,
                    'longitude': f.longitude,
                    'description': f.description
                }
                all_fac.append(fac)

        return all_fac

    def get_pos_info(self):
        '''
            Extract information of POS servers

            Returned Value:
                The json array of POS servers information
        '''

        all_pos = []

        # Start to query from POS data table
        for p in db.session.query(POS):
            # Find the POS server location which is same as user's.
            if p.city == self.location:
                pos = {
                    'id': p.id,
                    'district': p.district,
                    'method': p.partition_method,
                    'bound_Latlng1': p.bound_min_point,
                    'bound_Latlng2': p.bound_max_point,
                    'latitude': p.latitude,
                    'longitude': p.longitude,
                    'isContact': p.is_subscribe
                }
                all_pos.append(pos)

        return all_pos

    def update_db(self, POSInfo):
        '''
            Update information of POS servers

            POSInfo :
                The new update of POS server
        '''
        # Start to query from POS data table
        for p in db.session.query(POS):

            # Find the specified POS server
            if p.id == POSInfo["posName"]:
                sub_url = p.callback_url

                p.partition_method = POSInfo["posMethod"]
                if p.partition_method == 'District':

                    '''
                        Set value to null while method is "district"
                    '''
                    p.bound_min_point = ''
                    p.bound_max_point = ''
                else:
                    '''
                        Set value to text user send while method is "district"
                    '''
                    p.bound_min_point = POSInfo["boundMinPoint"]
                    p.bound_max_point = POSInfo["boundMaxPoint"]
        db.session.commit()
        return sub_url
