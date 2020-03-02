from app import create_app
import os

from make_datastore import create_datastore

# Determine config settings from environment variables.
config_name = os.getenv('FLASK_CONFIG') or 'development'

if __name__ == "__main__":

    app = create_app(config_name)

    location = app.config['SQLALCHEMY_DATABASE_URI']
    db_path = location.replace('sqlite:///', '')
    location = os.path.dirname(db_path)

    with app.app_context():        
        create_datastore(location)

    app.run(debug=True)  # , use_reloader=False)
