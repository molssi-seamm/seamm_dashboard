import sys
import os

INTERP = os.path.join(os.environ['HOME'], 'seamm_dashboard', 'venv', 'bin', 'python')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())
sys.path.append('Seamm_dashboard')


# create the production app for wsgi
os.environ['FLASK_CONFIG'] = 'production'
from results_dashboard import app as application
