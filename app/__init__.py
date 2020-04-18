import connexion

from flask_cors import CORS, cross_origin
from config import config
from flask_mongoengine import MongoEngine
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from .template_filters import replace_empty
# from flask_admin import Admin
# from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
from flask_moment import Moment
from .logger import setup_logging
import logging

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

mail = Mail()
cors = CORS()
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
# For: @app.route("/api/v1/users")
bootstrap = Bootstrap()
# app_admin = Admin(name='MolSSI Molecular Software DB Admin', template_mode='bootstrap3',
#                   base_template='admin/custom_base.html')

# login_manager = LoginManager()
# login_manager.login_view = 'auth.login'   # endpoint name for the login view
moment = Moment()
toolbar = DebugToolbarExtension()
#Base = declarative_base()

db = SQLAlchemy()
ma = Marshmallow()

logger = logging.getLogger()

def create_app(options):
    """Flask app factory pattern
      separately creating the extensions and later initializing"""

    conn_app = connexion.App(__name__, specification_dir='./')
    app = conn_app.app
    logger.info('Startup mode is ' + options.mode)
    logger.info(' Database = ' + config[options.mode].SQLALCHEMY_DATABASE_URI)
    app.config.from_object(config[options.mode])

    conn_app.add_api('swagger.yml')
    db.init_app(app)
    
    with app.app_context() as context:
        db.create_all()

    # init
    mail.init_app(app)
    cors.init_app(app)
    bootstrap.init_app(app)
    # login_manager.init_app(app)
    # app_admin.init_app(app)
    moment.init_app(app)
    # toolbar.init_app(app)

    # jinja template
    app.jinja_env.filters['empty'] = replace_empty

    # from .auth import auth as auth_blueprint
    # app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .routes.main import main as main_blueprint
    from .routes.jobs import jobs as jobs_blueprint
    from .routes.flowcharts import flowcharts as flowchart_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(jobs_blueprint)
    app.register_blueprint(flowchart_blueprint)
    # from .api import api as api_blueprint
    # app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    # To avoid circular import
    # from app.admin import add_admin_views
    # add_admin_views()

    return app

