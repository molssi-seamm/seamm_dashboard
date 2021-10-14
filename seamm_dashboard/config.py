"""Flask app configuration
"""
import os


class BaseConfig:

    _basedir = os.path.abspath(os.path.dirname(__file__))
    STATIC_FOLDER = "static"
    ADMINS = frozenset(["janash@vt.edu", "psaxe@vt.edu"])
    SECRET_KEY = "SecretKeyForSessionSigning"
    EDIT_SOFTWARE_SALT = "ThisIsAnotherSalt"
    THREADS_PER_PAGE = 8
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # email
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.googlemail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ["true", "on", "1"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "userhere")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "passhere")
    MAIL_SUBJECT_PREFIX = "[MolSSI Molecular Software DB]"
    MAIL_SENDER = "MolSSI Molecular DB Admin <info@molssi.org>"
    APP_ADMIN = os.environ.get("APP_ADMIN", "janash@vt.edu")
    EMAIL_CONFIRMATION_ENABLED = False

    # Client-side config
    API_RESULTS_PER_PAGE = 5

    # Jinia template
    REPLACE_NONE = ""
    GOOGLE_ANALYTICS_GTAG = "UA-116673029-1"
    GOOGLE_ANALYTICS_GTAG_submit = "UA-116673029-2"
    WTF_CSRF_ENABLED = True  # it's true by default, important to prevent CSRF attacks


class DevelopmentConfig(BaseConfig):
    _basedir = os.path.abspath(os.path.dirname(__file__))
    DEBUG = True
    TESTING = False
    WORDPRESS_DOMAIN = "http://localhost:8888"
    API_DOMAIN = "http://localhost:5000"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        _basedir, "data", "projects", "molssi_jobstore.db"
    )


class TestingConfig(BaseConfig):
    import tempfile

    DEBUG = True
    TESTING = True
    API_DOMAIN = "http://localhost:4000"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    initialize = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    WORDPRESS_DOMAIN = "http://molssi.org"
    API_DOMAIN = "http://api.molssi.org"
    MONGODB_SETTINGS = {
        "host": "mongodb://user:pass@xyz.mlab.com:27163/resources_website",
    }


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
}
