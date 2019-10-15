# MolSSI Dashboard (Flask-coreUI)

This application is a results Dashborad for MolSSI projects.

The server runs Flask on Passenger and Apache, or can run flask testing server.

### Run the Development Web Server
Create a virtual environment and start the local app.

```
conda create -n results_dashboard_env python=3.6.1 pip
source activate results_dashboard_env
pip install -r requirements.txt
python results_dashboard.py
```

```
# If you have anaconda as your default, make sure to run
conda install virtualenv
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
python results_dashboard.py
```
