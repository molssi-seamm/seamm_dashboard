from app import create_app
from werkzeug.middleware.profiler import ProfilerMiddleware
# from flask_migrate import Migrate, upgrade
import os
from dotenv import load_dotenv

from app.models.sqlalchemy.jobstore import DataStore

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Determine config settings from environment variables.
config_name = os.getenv('FLASK_CONFIG') or 'development'

app = create_app(config_name)

# if app.config['TESTING']:
#     app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])

# migrate = Migrate(app, db)

def create_datastore(location):

    location = os.path.abspath(location)
    datastore_location = os.path.join(location, 'molssi_jobstore.db')
    db = DataStore(datastore_location)

    for job in os.listdir(location):
        
        job_path = os.path.abspath(os.path.join(location, job))
        if os.path.isdir(job_path):
            db.add_job(job_path)
    
    db.Session().close()


if __name__ == "__main__":
    datastore_location = os.path.join("data", "examples")
    create_datastore(datastore_location)
    app.run(debug=True)  # , use_reloader=False)
