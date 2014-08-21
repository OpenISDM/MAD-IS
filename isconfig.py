import os

_basedir = os.path.abspath(os.path.dirname(__file__))

# Create dummy secrey key so we can use sessions
SECRET_KEY = '123456790'
DATABASE_FILE = 'is_db.sqlite'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, DATABASE_FILE)
SQLALCHEMY_ECHO = True
DATABASE_PATH = os.path.join(_basedir, DATABASE_FILE)
DATABASE_CONNECT_OPTIONS = {}

del os