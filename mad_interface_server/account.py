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
from flask import redirect, url_for, request
from flask.ext import admin, login
from flask.ext.admin import expose, helpers
from flask.ext.admin.contrib import sqla

from mad_interface_server import app
from mad_interface_server.custom_form import LoginForm, RegistrationForm
from mad_interface_server import database
from mad_interface_server.file_system import FileSystem 

show_menu = False
fs = FileSystem()


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
        return database.db.session.query(database.User).get(user_id)


def init_admin():
    # Create admin
    global admin
    admin = admin.Admin(app, 'MAD-IS', index_view=MyAdminIndexView())
    admin.add_view(PosView(database.POS, database.db.session))
    admin.add_view(FacView(database.Facility, database.db.session))


class PosView(sqla.ModelView):
    # list_template = 'admin/home.html'

    '''
        Create customized model view class.
    '''
    column_searchable_list = ('id',)
    # list_template = 'list_pos.html'

    @expose('/delete', methods=('GET', 'POST'))
    def deleteAll_view(self):
        database.db.session.query(POS).delete()
        database.db.session.commit()

        return redirect(url_for('.index_view'))

    def is_visible(self):
        return False


class FacView(sqla.ModelView):
    # list_template = 'admin/home.html'

    '''
        Create customized model view class.
    '''
    column_searchable_list = ('id',)
    list_template = 'list_fac.html'

    @expose('/delete', methods=('GET', 'POST'))
    def deleteAll_view(self):
        database.db.session.query(Facility).delete()
        database.db.session.commit()

        return redirect(url_for('.index_view'))

    def is_visible(self):
        return False


class MyAdminIndexView(admin.AdminIndexView):

    """
        Create customized index view class that handles
        login & registratio & setup
    """
    @expose('/')
    def index(self):

        global show_menu
        """
            if user have not been authenticated, got to login view.
        """
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login_view'))

        """
            Find user, and if there have not setting about country,
            start the setup.Otherwise, enter the view that have already
            setup.
        """
        for u in database.db.session.query(database.User):
            if login.current_user.get_id() == u.id:
                if u.is_finish_setup is False:
                    show_menu = False
                    return redirect(url_for('.setup_view'))
                else:
                    show_menu = True

        return redirect(url_for('.home_view'))

        # return super(MyAdminIndexView, self).index()

    @expose('/setup/')
    def setup_view(self):
        """
            Setup View, and if there have not setting about country,
            start the setup.Otherwise, enter the view that have
            already finished the setup.
        """
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        else:
            return self.render('admin/setup.html')

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
        link = '<p>Don\'t have an account? <a href="' + \
            url_for('.register_view') + '">Click here to register.</a></p>'
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
            user = database.User(is_finish_setup=False)

            form.populate_obj(user)

            database.db.session.add(user)
            database.db.session.commit()

            login.login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + \
            url_for('.login_view') + '">Click here to log in.</a></p>'
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

    @expose('/home/')
    def home_view(self):
        return self.render('admin/home.html')


class Home(admin.BaseView):

    """
        Create customized index view class that handles
        the monitor of POS servers status
    """
    @admin.expose('/')
    def index(self):
        return self.render('home.html')

    def is_accessible(self):
        return login.current_user.is_authenticated()

    def is_visible(self):
        if show_menu is True:
            return True
        else:
            return False

