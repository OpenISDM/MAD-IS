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

#-*- coding: utf-8 -*-
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
from fileSystem import FileSystem
import os
import json2rdf
import xml.etree.ElementTree as ET
import requests
import socket

# Create Flask application
app = Flask(__name__)

#app.register_blueprint(action)
app.register_blueprint(demand)
# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create in-memory database
app.config['DATABASE_FILE'] = 'sample_db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

fs = FileSystem()
show_menu = False;
# Create user model. For simplicity, it will store passwords in plain text.
class User(db.Model):

    '''
       Create user model. For simplicity, it will store passwords in plain text.
    '''
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(64))
    country = db.Column(db.String(32))
    city = db.Column(db.String(32))
    is_finish_setup1 = db.Column(db.Boolean, nullable=False)
    is_finish_setup2 = db.Column(db.Boolean, nullable=False)
    is_finish_setup3 = db.Column(db.Boolean, nullable=False)
    #ui_language = db.Column(db.String(32))

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

class LoginForm(form.Form):
    '''
        Define login forms
    '''
    login = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(login=self.login.data).first()

class RegistrationForm(form.Form):

    '''
        Define Registration forms
    '''
    login = fields.TextField(validators=[validators.required()])
    email = fields.TextField()
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        if db.session.query(User).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Duplicate username')

def init_login():

    '''
        Initialize flask-login
    '''
    login_manager = login.LoginManager()
    login_manager.init_app(app)


    '''
        Create user loader function
    '''
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)

class MyModelView(sqla.ModelView):

    '''
        Create customized model view class.
    '''
    def is_accessible(self):
        return login.current_user.is_authenticated()

    def is_visible(self):
        if show_menu == True:
            return True
        else :
            return False

class MyAdminIndexView(admin.AdminIndexView):
    '''
        Create customized index view class that handles login & registration & setup
    '''
    @expose('/')
    def index(self):
        '''
            Enter the index View.
        '''
        global show_menu
        if not login.current_user.is_authenticated():
            '''
                if user have not been authenticated, got to login view.
            '''
            return redirect(url_for('.login_view'))

        # Start to query the match user
        for u in db.session.query(User):
            if login.current_user.get_id() == u.id:
                '''
                    Find user, and if there have not setting about country, start the setup.
                    Otherwise, enter the view that have already setup.
                '''
                if u.is_finish_setup1 == False:
                    show_menu = False
                    return redirect(url_for('.setup_view',step='step1'))
                elif u.is_finish_setup2 == False :
                    show_menu = False
                    return redirect(url_for('.setup_view',step='step2'))
                elif u.is_finish_setup3 == False :
                    show_menu = False
                    return redirect(url_for('.setup_view',step='step3'))
                else :
                    show_menu = True

        return super(MyAdminIndexView, self).index()


    @expose('/setup/<step>')
    def setup_view(self,step):
        '''
            Setup View, and if there have not setting about country, start the setup.
            Otherwise, enter the view that have already finished the setup.
        '''
        if step == 'step1':
            return self.render('admin/setup1.html')
        if step == 'step2':
            return self.render('admin/setup2.html')
        if step == 'step3':
            return self.render('admin/setup3.html')


    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        '''
            Handle user login
        '''
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):

            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated():
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):

        '''
            Handle user register
        '''
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = User(is_finish_setup1=False,is_finish_setup2=False,is_finish_setup3=False)

            form.populate_obj(user)

            db.session.add(user)
            db.session.commit()

            login.login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        '''
            Handle user logout
        '''
        login.logout_user()
        return redirect(url_for('.index'))

class MonitorView(admin.BaseView):
    '''
        Create customized index view class that handles the monitor of POS servers status
    '''
    @admin.expose('/')
    def index(self):
        return self.render('monitor.html')

    def is_accessible(self):
        return login.current_user.is_authenticated()

    def is_visible(self):
        if show_menu == True:
            return True
        else :
            return False

class ImportDataView(admin.BaseView):
    '''
        Create customized index view class that handles the monitor of POS servers status
    '''
    @admin.expose('/')
    def index(self):
        return self.render('InputFacData.html')

    def is_accessible(self):
        return login.current_user.is_authenticated()

    def is_visible(self):
        if show_menu == True:
            return True
        else :
            return False


class ContactView(admin.BaseView):
    @admin.expose('/')
    def index(self):
        return self.render('contact.html')

    def is_accessible(self):
        return login.current_user.is_authenticated()


    def is_visible(self):
        if show_menu == True:
            return True
        else :
            return False

class Information:
    '''
        The class "information" allow you/me insert and extract data.
    '''
    def __init__(self):

        '''
            Initialize user and its city and country he/she serve
        '''
        self.user = User.query.filter_by(id=login.current_user.get_id()).first()
        self.country=self.user.country
        self.city=self.user.city


    def store_location(self,country,city):
        '''
            Store user's location when sending the registration form.
        '''
        self.user.country=country
        self.user.city=city
        db.session.commit()

    def finish_setup_step(self,step):
        if step == "step1":
            self.user.is_finish_setup1=True
        elif step == "step2":
            self.user.is_finish_setup2=True
        elif step == "step3":
            self.user.is_finish_setup3=True
        else:
            pass
        db.session.commit()

    def get_config(self,configdir):
        '''
            Get configuration file's content

            configdir:
                configuration file's directory

            filename:
                configuration file's path

            Returned Value:
                If the function find the file, the returned is a json object of configuration content;
                otherwise, the returned value is null.
        '''
        filename = configdir+'/'+self.country+'/'+self.city+'.ini'
        if os.path.exists(filename):
            # if file is exist, get its content.
            config = ConfigObj(filename)
            config_info = {
                "coordinates" : config['Country Information']['Origin Of Coordinates'],
                "wardpath" : config['Country Information']['District Info Path'],
                "key" : config['Boundary']['ApiKey'],
                "posCountryCode" : config['POS Information']['POS_country_code']
            }
            return config_info
        else:
            # file is not exist, return null.
            return 'Null'

    def create_config(self,mydir,coordinate,key):
        '''
            Create the configuration file

            mydir:
                server's path

            coordinate :
                the original coordinate of city

            key:
                The cloud document ID

            Returned Value:
                If the function find the file, the returned is a json object of configuration content;
                otherwise, the returned value is null.
        '''

        config = ConfigObj()
        config.filename = mydir+'/ConfigFile/'+self.country+'/'+self.city+'.ini'
        config['Country Information']={}
        config['Country Information']['Origin Of Coordinates']=coordinate
        config['Country Information']['District Info Path']=mydir+"/District Info/"+self.city+'.xml'
        config['Boundary']={}
        config['Boundary']['ApiKey']=key
        config['POS Information']={}
        config['POS Information']['POS_country_code']=""
        config.write()

    def get_district(self,key,mydir):
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
            tree = ET.parse(mydir+'/District Info/'+self.city+'.xml')
            root = tree.getroot()
            for info in root.findall('District'):
                data = {
                          "District" : info.find("Name").text,
                          "Code" : info.find("PostalCode").text
                      }
                region_info.append(data)
            return region_info
        else :
            return 'Null'

    def store_db(self,content,server_location):

        '''
            Store information of POS servers and facilities

            content :
                data that will be inserted to database

            server_location:
                server's path
        '''

        if content[1] == 'posServer':

            '''
                Store information of POS server
            '''
            topic_path = server_location + '/static/Topic/'+content[3]
            pos = POS(id=content[3],city=self.city,
                      district=content[4].decode('utf8'),
                      partition_method='District',
                      latitude=content[5],longitude=content[6],
                      topic_dir=topic_path,is_subscribe=False)

            db.session.add(pos)

        elif content[1] == 'facility':
            '''
                Store information of facility
            '''

            facility = Facility(city=self.city,id=content[2],
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

    def get_facility_info(self):

        '''
            Extract information of facilities servers

            Returned Value:
                The json array of facilities information
        '''

        all_fac = []
        # Start to query from Facility data table
        for f in db.session.query(Facility):
            if f.city == self.city:
                fac={
                    'id' : f.id,
                    'name' : f.name,
                    'type' : f.type,
                    'category' : f.category,
                    'district' : f.district,
                    'address' : f.address,
                    'telephone' : f.telephone,
                    'latitude' : f.latitude,
                    'longitude' : f.longitude,
                    'description' : f.description
                }
                all_fac.append(fac)
            else:
                all_fac = []

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
            #Find the POS server location which is same as user's.
            if p.city == self.city:
                pos={
                    'id' : p.id,
                    'district' : p.district,
                    'method' : p.partition_method,
                    'bound_Latlng1' : p.bound_min_point,
                    'bound_Latlng2' : p.bound_max_point,
                    'latitude' : p.latitude,
                    'longitude' : p.longitude,
                    'isContact' : p.is_subscribe
                }
                all_pos.append(pos)
            else:
                all_fac = []

        return all_pos

    def update_db(self, POSInfo):
        '''
            Update information of POS servers

            POSInfo :
                The new update of POS server
        '''

        # Start to query from POS data table
        for p in db.session.query(POS):

            #Find the specified POS server
            if p.id == POSInfo[1]:
                sub_url = p.callback_url

                p.partition_method = POSInfo[2]
                if p.partition_method == 'District':

                    '''
                        Set value to null while method is "district"
                    '''
                    p.bound_min_point = ''
                    p.bound_max_point = ''
                else :
                    '''
                        Set value to text user send while method is "district"
                    '''
                    p.bound_min_point = POSInfo[3]
                    p.bound_max_point = POSInfo[4]
        db.session.commit()
        return sub_url

def determine_topic_and_hub(pos_id,pos_type):

    '''
        Decide which topic address and hub address will be assigned the subscriber and
        return the json object that include their values.

        pos_id: The POS server ID

        pos_type:
            The fix type or mobile type of POS server
    '''

    reply ={
            'hub_url': fs.my_web_addr + '/subscribe/',
    }

    reply['topic_url'] = 'Not found'

    if pos_type == 'fix':
        for p in db.session.query(POS):
            if p.id == pos_id:
                reply['topic_url']= p.topic_dir
    elif pos_type == 'mobile':
        print 'testing'

    return reply

def match_url(topic_url):

    '''
        Decide which topic address and hub address will be assigned the subscriber and
        return the json object that include their values.

        pos_id: The POS server ID

        pos_type:
            The fix type or mobile type of POS server
    '''

    is_find = False
    for p in db.session.query(POS):
        if p.topic_dir == topic_url:
            is_find = True
    return is_find

def store_subscriber(topic_url,callback_url):
    for p in db.session.query(POS):
        if p.topic_dir == topic_url:
            p.callback_url = callback_url
            p.is_subscribe = True
            db.session.commit()
    print 'have stored the subscription'

def content_distribution(sub_url):
    if sub_url is not None:
        for p in db.session.query(POS):
            if p.callback_url == sub_url:
                pos_id = p.id
        topic_dictionary = {
            'png': fs.my_topic_dir + pos_id +'/' + pos_id +'.png',
            'rdf'  : fs.my_topic_dir + pos_id +'/' + pos_id +'.rdf'
        }



        for x in topic_dictionary:
            files = {'file': open(topic_dictionary[x], 'rb')}
            r = requests.post(sub_url, files=files)

    else:
        print "This POS server have not subscribed"

# Flask views
@app.route('/')
def index():
    return render_template('index.html')


# Initialize flask-login
init_login()

# Create admin
admin = admin.Admin(app, 'MAD-IS', index_view=MyAdminIndexView(), base_template='my_master.html')
#admin = admin.Admin(index_view=MyAdminIndexView())
admin.add_view(MonitorView(name="Monitor"))

admin.add_view(ImportDataView(category='Data'))
admin.add_view(MyModelView(POS, db.session, category='Data'))
admin.add_view(MyModelView(Facility, db.session, category='Data'))
admin.add_view(ContactView(name='Contact Us'))

def build_sample_db():
    """
        Populate a db with some entries.
    """

    import string

    db.drop_all()
    db.create_all()
    test_user = User(login="test", password="test",
                     is_finish_setup1=False,is_finish_setup2=False,
                     is_finish_setup3=False)
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


def answer(request):
    info = Information()

    jsonText = {'status' : 'OK',
                'country' : info.country,
                'city' : info.city}

    if request == 'cityInfo':
        data = info.get_config(fs.mydir+'/ConfigFile')
    elif request == 'geoInfo':
        data = info.get_district('district',fs.mydir)
    elif request == 'exist_Country&City':
        data = fs.search_dir_file('/ConfigFile')
    elif request == 'setupInfo':
        data = info.get_facility_info()
        config_info = info.get_config(fs.mydir+'/ConfigFile')
        ward_info = info.get_district('district',fs.mydir)
        pos_info = info.get_pos_info()
        jsonText['configInfo']=config_info
        jsonText['wardInfo']=ward_info
        jsonText['posInfo']=pos_info

    jsonText['data']=data

    return jsonText

def bulid_info(string):
    info = Information()
    my_ip_address = '140.109.22.197'
    topic_path = '/static/Topic/'
    if string[0]=='location':
        info.store_location(string[1],string[2])
        fs.create_folder('/ConfigFile/'+string[1])
        info.finish_setup_step('step1')
    elif string[0]=='geo':
        info.create_config(fs.mydir,string[1],string[2])
        fs.create_xml_file(info.city,string[3])
        info.finish_setup_step('step2')
    elif string[0]=='data':
        info.store_db(string,fs.my_web_addr)
        info.finish_setup_step('step3')
    elif string[0]=='update':
        sub_url = info.update_db(string)
        rdf_text = json2rdf.generate_rdf_text(string[5])
        fs.download_file(topic_path,string[1],'rdf',rdf_text,'w')
        fs.download_file(topic_path,string[1],'png',string[6],'wb')
        print sub_url
        content_distribution(sub_url)
    elif string[0]=='download':
        fs.create_folder(topic_path+string[1])
        rdf_text = json2rdf.generate_rdf_text(string[2])
        fs.download_file(topic_path,string[1],'rdf',rdf_text,'w')
        fs.download_file(topic_path,string[1],'png',string[3],'wb')

if __name__ == '__main__':
    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()

    # Start app
    #app.run(host= fs.my_web_addr, port=int("80"), debug=True)
    app.run(host= socket.gethostbyname(socket.gethostname()), port=int("80"))


