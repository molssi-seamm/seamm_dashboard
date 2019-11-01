from app import create_app
from werkzeug.contrib.profiler import ProfilerMiddleware
import os
import glob


# Determine config settings from environment variables.
config_name = os.getenv('FLASK_CONFIG') or 'development'

app = create_app(config_name)

if __name__ == "__main__":
    app.run(debug=True)  # , use_reloader=False)
