from app import create_app, db
from werkzeug.middleware.profiler import ProfilerMiddleware
# from flask_migrate import Migrate, upgrade
import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Determine config settings from environment variables.
config_name = os.getenv('FLASK_CONFIG') or 'development'

app = create_app(config_name)

# if app.config['TESTING']:
#     app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])

# migrate = Migrate(app, db)


if __name__ == "__main__":
    app.run(debug=True)  # , use_reloader=False)
