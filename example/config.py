import os
import binascii
from tempfile import gettempdir


def basedir():
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig(object):
    SITE_NAME = 'Default'
    DEBUG = False
    TESTING = False
    SECRET_KEY = binascii.hexlify(os.urandom(24))

    # flask-sqlalchemy
    DATABASE_URI = 'sqlite://'     # in memory
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False
    DATABASE_URI = 'sqlite://{0}/myapp.db'.format(gettempdir())

    SQLALCHEMY_ECHO = True

    prose = 'sqlite:///' + os.path.join(os.getcwd(), 'prose.db')
    security = 'sqlite:///' + os.path.join(os.getcwd(), 'security.db')

    SQLALCHEMY_BINDS = {
        'prose': prose,
        'security': security,
    }

    print(SQLALCHEMY_BINDS)

    # celery settinngs
    BROKER_TRANSPORT = 'redis'
    BROKER_URL = 'redis://127.0.0.1:6379/0'
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'

    #config flask-security
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True


config = {
    'dev':  'config.DevelopmentConfig',
    'default': 'config.DevelopmentConfig',
}


def configure_app(app):
    # set MYAPP_CONFIG in the apache httpd.conf file using SetEnv
    selected_config = os.getenv('MYAPP_CONFIG', 'default')
    app.config.from_object(config[selected_config])
    app.config.from_pyfile('settings.cfg', silent=False)
