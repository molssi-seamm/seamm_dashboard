import logging
import os
import time

import connexion
import configargparse

# from flask_admin import Admin
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_authorize import Authorize
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_current_user,
    get_jwt_identity,
)

from config import config
from .template_filters import replace_empty
from .setup_logging import setup_logging
from .setup_argparsing import options

from .authorize_patch import Authorizer

# Setup the logging, now that we know where the datastore is
datastore = options.datastore
setup_logging(datastore, options)
logger = logging.getLogger("dashboard")

# Two of the Flask options cannot be reset, and should (apparently) be
# handled with environment variables ... so if they are in the options
# set the correct environment variables. Carefully!

if "env" in options:
    if "FLASK_ENV" in os.environ and options.env != os.environ["FLASK_ENV"]:
        logger.warning(
            (
                "The environment variable FLASK_ENV is being overidden by "
                "the configuration option 'env' ({})"
            ).format(options.env)
        )
    os.environ["FLASK_ENV"] = options.env
if "debug" in options:
    if "FLASK_DEBUG" in os.environ and options.debug != os.environ["FLASK_DEBUG"]:
        logger.warning(
            (
                "The environment variable FLASK_DEBUG is being overidden by "
                "the configuration option 'debug' ({})"
            ).format(options.debug)
        )
    os.environ["FLASK_DEBUG"] = options.debug

# continue the setup
mail = Mail()
cors = CORS()

bootstrap = Bootstrap()

jwt = JWTManager()
authorize = Authorize(current_user=get_current_user)

moment = Moment()
toolbar = DebugToolbarExtension()

db = SQLAlchemy()
ma = Marshmallow()


def create_app(config_name=None):
    """Flask app factory pattern
    separately creating the extensions and later initializing"""

    conn_app = connexion.App(__name__, specification_dir="./")
    app = conn_app.app

    logger.info("")
    if config_name is not None:
        logger.info("Configuring from configuration " + config_name)
        app.config.from_object(config[config_name])

        options.initialize = False
        options.no_check = True
    else:
        # Report where options come from
        parser = configargparse.get_argument_parser("dashboard")
        logger.info("Where options are set:")
        logger.info(60 * "-")
        for line in parser.format_values().splitlines():
            logger.info(line)

        # Now set the options!
        logger.info("")
        logger.info("Configuration:")
        logger.info(60 * "-")
        for key, value in vars(options).items():
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

    conn_app.add_api("swagger.yml")

    db.init_app(app)
    with app.app_context():
        if options.initialize:
            logger.info("Removing all previous jobs from the database.")
            db.drop_all()
        db.create_all()

        from .auth import auth as auth_blueprint

        app.register_blueprint(auth_blueprint)

        from .routes.main import main as main_blueprint
        from .routes.jobs import jobs as jobs_blueprint
        from .routes.flowcharts import flowcharts as flowchart_blueprint
        from .routes.projects import projects as project_blueprint

        from .routes.main import errors

        app.register_blueprint(main_blueprint)
        app.register_blueprint(jobs_blueprint)
        app.register_blueprint(flowchart_blueprint)
        app.register_blueprint(project_blueprint)

        app.register_error_handler(404, errors.not_found)

    # init
    mail.init_app(app)
    cors.init_app(app)
    bootstrap.init_app(app)
    authorize.init_app(app)
    jwt.init_app(app)
    # app_admin.init_app(app)
    moment.init_app(app)
    # toolbar.init_app(app)

    # jinja template
    app.jinja_env.filters["empty"] = replace_empty

    # Authorization configuration
    app.config["AUTHORIZE_DEFAULT_PERMISSIONS"] = dict(
        owner=["read", "update", "delete", "create"],
        group=["read", "update"],
        other=[""],
    )
    app.config["AUTHORIZE_ALLOW_ANONYMOUS_ACTIONS"] = True

    # Set application to store JWTs in cookies.
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]

    # Set the cookie paths
    app.config["JWT_ACCESS_COOKIE_PATH"] = "/api"
    app.config["JWT_REFRESH_COOKIE_PATH"] = "/api/auth/token/refresh"

    # Cookie security
    app.config["JWT_COOKIE_SECURE"] = False
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    # To avoid circular import
    # from app.admin import add_admin_views
    # add_admin_views()

    logger.info("")
    logger.info("Final configuration:")
    logger.info(60 * "-")
    for key, value in app.config.items():
        logger.info("\t{:>30s} = {}".format(key, value))
    logger.info("")

    if not options.no_check:
        # Ugly but avoids circular import.
        from .models.import_jobs import import_jobs

        t0 = time.perf_counter()
        with app.app_context():
            n_projects, n_added_projects, n_jobs, n_added_jobs = import_jobs(
                os.path.join(options.datastore, "projects")
            )
        t1 = time.perf_counter()
        logger.info(
            "Checked {} jobs and {} projects in {:.2f} s.".format(
                n_jobs, n_projects, t1 - t0
            )
        )
        if n_added_jobs > 0 or n_added_projects > 0:
            logger.info(
                "  added {} jobs and {} projects".format(n_added_jobs, n_added_projects)
            )

    logger.info(f'{app.url_map}')

    return app
