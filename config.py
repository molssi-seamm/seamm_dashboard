"""Flask app configuration
"""
import os

class BaseConfig:

    _basedir = os.path.abspath(os.path.dirname(__file__))
    STATIC_FOLDER = 'static'
    ADMINS = frozenset(['daltarawy@vt.edu'])  ##
    SECRET_KEY = 'SecretKeyForSessionSigning'
    EDIT_SOFTWARE_SALT = 'ThisIsAnotherSalt'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'data', 'projects', 'molssi_jobstore.db')
    THREADS_PER_PAGE = 8


    # email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'userhere')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'passhere')
    MAIL_SUBJECT_PREFIX = '[MolSSI Molecular Software DB]'
    MAIL_SENDER = 'MolSSI Molecular DB Admin <info@molssi.org>'
    APP_ADMIN = os.environ.get('APP_ADMIN', 'daltarawy@vt.edu')
    EMAIL_CONFIRMATION_ENABLED = False

    # Client-side config
    API_RESULTS_PER_PAGE = 5

    # Jinia template
    REPLACE_NONE = ''
    GOOGLE_ANALYTICS_GTAG = 'UA-116673029-1'
    GOOGLE_ANALYTICS_GTAG_submit = 'UA-116673029-2'
    WTF_CSRF_ENABLED = True   # it's true by default, important to prevent CSRF attacks

class SEAMMConfig(BaseConfig):
    _seamm_home = os.path.join(os.path.expanduser("~"), ".seamm")

    _seamm_ini = os.path.join(_seamm_home, "seamm.ini")

    # Should move this into a function.
    # This section reads a seamm settings file.
    if os.path.exists(_seamm_ini):
        _datastore_location = None
        with open(_seamm_ini) as f:
            settings = f.readlines()
            for line in settings:
                if 'datastore' in line.lower():
                    _datastore_location = line.split('=')[1].strip()
                
            if not _datastore_location:
                raise AttributeError('No datastore location found in seamm.ini file!')
    
        _datastore_location = os.path.expanduser(_datastore_location)

        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_datastore_location, 'projects', 'molssi_jobstore.db')

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False
    WORDPRESS_DOMAIN = 'http://localhost:8888'
    API_DOMAIN = 'http://localhost:5000'
    MONGODB_SETTINGS = {
        'host': "mongodb://ninja:pass@localhost:27017/resources_website",  # URI
        # 'db': 'project1',
        # 'host': 'localhost',
        # 'port': 12345,
        # 'username': 'ninja',
        # 'password': '123'
    }


class TestingConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    WORDPRESS_DOMAIN = 'http://molssi.org'
    API_DOMAIN = 'http://molssi-api.herokuapp.com'
    MONGODB_SETTINGS = {
        'host': "mongodb://ninja:pass@xyz.mlab.com:27163/resources_website"
    }


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    WORDPRESS_DOMAIN = 'http://molssi.org'
    API_DOMAIN = 'http://api.molssi.org'
    MONGODB_SETTINGS = {
        'host': "mongodb://user:pass@xyz.mlab.com:27163/resources_website",
    }


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'seamm': SEAMMConfig,
    # 'docker': DockerConfig,

    'default': DevelopmentConfig
}
