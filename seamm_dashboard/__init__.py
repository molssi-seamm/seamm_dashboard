import logging
import os
from pathlib import Path

import connexion

# from flask_admin import Admin
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from flask_authorize import Authorize

from .jwt_patch import flask_jwt_extended

from .config import config
from .template_filters import replace_empty
from .setup_logging import setup_logging
from .setup_argparsing import options, parser


# Handle versioneer
from ._version import get_versions

__author__ = """Jessica Nash"""
__email__ = "janash@vt.edu"
versions = get_versions()
__version__ = versions["version"]
__git_revision__ = versions["full-revisionid"]
del get_versions, versions

# Ensure that the projects directory exists.
datastore_path = Path(options["datastore"]).expanduser().resolve()
datastore = str(datastore_path)
datastore_path.mkdir(parents=True, exist_ok=True)

# Setup the logging, now that we know where the datastore is
setup_logging(datastore, options)
logger = logging.getLogger("dashboard")

# If there is no database we need to initialize!
db_path = datastore_path / "seamm.db"
if not db_path.exists():
    logger.warning("The database does not exists, so forcing initialization")
    options["initialize"] = True

# Two of the Flask options cannot be reset, and should (apparently) be
# handled with environment variables ... so if they are in the options
# set the correct environment variables. Carefully!

if "env" in options:
    if "FLASK_ENV" in os.environ and options["env"] != os.environ["FLASK_ENV"]:
        logger.warning(
            (
                "The environment variable FLASK_ENV is being overidden by "
                "the configuration option 'env' ({})"
            ).format(options["env"])
        )
    os.environ["FLASK_ENV"] = options["env"]
if "debug" in options:
    if "FLASK_DEBUG" in os.environ and options["debug"] != os.environ["FLASK_DEBUG"]:
        logger.warning(
            (
                "The environment variable FLASK_DEBUG is being overidden by "
                "the configuration option 'debug' ({})"
            ).format(options["debug"])
        )
    os.environ["FLASK_DEBUG"] = options["debug"]

# continue the setup
mail = Mail()
cors = CORS()

bootstrap = Bootstrap()

jwt = flask_jwt_extended.JWTManager()
authorize = Authorize(current_user=flask_jwt_extended.get_current_user)
moment = Moment()
toolbar = DebugToolbarExtension()

db = SQLAlchemy()
ma = Marshmallow()


@jwt.user_lookup_loader
def user_loader_callback(jwt_header, jwt_payload):
    """Function for app, to return user object"""

    if jwt_header:
        from seamm_datastore.database.models import User

        username = jwt_payload["sub"]["username"]
        user = User.query.filter_by(username=username).one_or_none()

        return user
    else:
        # return None / null
        return None


def create_app(config_name=None):
    """Flask app factory pattern
    separately creating the extensions and later initializing"""

    conn_app = connexion.App(__name__, specification_dir="./")
    app = conn_app.app

    logger.info("")
    if config_name is not None:
        logger.info("Configuring from configuration " + config_name)
        app.config.from_object(config[config_name])

        options["initialize"] = False
        options["no_check"] = True
    else:
        # Report where options come from
        # parser = configargparse.get_argument_parser("dashboard")
        logger.info("Where options are set:")
        logger.info(60 * "-")
        for section, tmp in parser.get_options().items():
            origin = parser.get_origins(section)
            for key, value in tmp.items():
                logger.info(f"{key:<19} {origin[key]:<15} {value}")

        # Now set the options!
        logger.info("")
        logger.info("Configuration:")
        logger.info(60 * "-")
        for key, value in options.items():
            if key not in (
                "env",
                "debug",
                "initialize",
                "log_dir",
                "log_level",
                "console_log_level",
                "dashboard_configfile",
            ):
                key = key.upper()
                if isinstance(value, str):
                    value = value.replace("%datastore%", datastore)
                logger.info("\t{:>30s} = {}".format(key, value))
                app.config[key] = value

    logger.info("")

    logger.info(
        "Running in "
        + app.config["ENV"]
        + " mode with database "
        + app.config["SQLALCHEMY_DATABASE_URI"]
    )

    # Authorization configuration
    app.config["AUTHORIZE_DEFAULT_PERMISSIONS"] = dict(
        owner=["read", "update", "delete", "create", "manage"],
        group=["read", "update"],
        other=[""],
    )
    app.config["AUTHORIZE_ALLOW_ANONYMOUS_ACTIONS"] = True

    # Set application to store JWTs in cookies.
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]

    # Set the cookie paths
    # app.config["JWT_ACCESS_COOKIE_PATH"] = "/api"
    app.config["JWT_REFRESH_COOKIE_PATH"] = "/api/auth/token/refresh"

    # Cookie security
    app.config["JWT_COOKIE_SECURE"] = False
    app.config["JWT_COOKIE_CSRF_PROTECT"] = True
    app.config["JWT_CSRF_ACCESS_PATH"] = "/api/"

    conn_app.add_api("swagger.yml")
    db.init_app(app)
    with app.app_context():
        from seamm_datastore.database.build import import_datastore, _build_initial

        if options["initialize"] or config_name and config_name.lower() == "testing":
            logger.warning("Removing all previous jobs from the database.")
            db.drop_all()
            db.create_all()
            # Create database using other interface for consistency.
            logger.info("Importing jobs...")
            _build_initial(db.session, "default")

        if config_name is None or not config_name.lower() == "testing":
            # Log in as user running
            import flask_authorize.plugin
            from seamm_datastore.database.models import User

            flask_authorize.plugin.CURRENT_USER = User.query.filter_by(id=2).one
            temp_path = os.path.join(
                os.path.expanduser(options["datastore"]), "projects"
            )
            logger.warning("Importing any jobs into the database.")
            import_datastore(db.session, temp_path)

            flask_authorize.plugin.CURRENT_USER = flask_jwt_extended.get_current_user

        from .routes.auth import auth as auth_blueprint
        from .routes.main import main as main_blueprint
        from .routes.jobs import jobs as jobs_blueprint
        from .routes.flowcharts import flowcharts as flowchart_blueprint
        from .routes.projects import projects as project_blueprint
        from .routes.admin import admin as admin_blueprint

        from .routes.main import errors

        app.register_blueprint(auth_blueprint)
        app.register_blueprint(main_blueprint)
        app.register_blueprint(jobs_blueprint)
        app.register_blueprint(flowchart_blueprint)
        app.register_blueprint(project_blueprint)
        app.register_blueprint(admin_blueprint)

        app.register_error_handler(404, errors.not_found)

    # init
    mail.init_app(app)
    cors.init_app(app)
    bootstrap.init_app(app)
    authorize.init_app(app)
    jwt.init_app(app)
    moment.init_app(app)

    # jinja template
    app.jinja_env.filters["empty"] = replace_empty

    logger.info("")
    logger.info("Final configuration:")
    logger.info(60 * "-")
    for key, value in app.config.items():
        logger.info("\t{:>30s} = {}".format(key, value))
    logger.info("")

    logger.info(f"{app.url_map}")
    return app
