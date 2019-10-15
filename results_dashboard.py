from app import create_app
from werkzeug.contrib.profiler import ProfilerMiddleware
import os
import glob

from app.models.sqlalchemy import DataStore


# Determine config settings from environment variables.
config_name = os.getenv('FLASK_CONFIG') or 'development'

app = create_app(config_name)

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
