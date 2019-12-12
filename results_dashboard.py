from app import create_app
from werkzeug.contrib.profiler import ProfilerMiddleware
import os

from make_datastore import create_datastore

# Determine config settings from environment variables.
config_name = os.getenv('FLASK_CONFIG') or 'development'


if __name__ == "__main__":

    app = create_app(config_name)

    if True:
        location = app.config['SQLALCHEMY_DATABASE_URI']
        location = os.path.dirname(location.replace('sqlite:///', ''))
        create_datastore(location)

    app.run(debug=True)  # , use_reloader=False)
