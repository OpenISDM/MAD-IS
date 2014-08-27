import os
import socket
_basedir = os.path.abspath(os.path.dirname(__file__))

# Create dummy secrey key so we can use sessions
SECRET_KEY = '123456790'
DATABASE_FILE = 'is_db.sqlite'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, DATABASE_FILE)
SQLALCHEMY_ECHO = True
DATABASE_PATH = os.path.join(_basedir, DATABASE_FILE)
DATABASE_CONNECT_OPTIONS = {}
# Directory & ip address
APP_DIR = os.path.abspath('mad_interface_server')
TOPIC_DIR = APP_DIR + '/static/Topic/'
WEB_URL = 'http://'+socket.gethostbyname(socket.gethostname())

del os