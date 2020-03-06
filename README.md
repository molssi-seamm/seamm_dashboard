# MolSSI Dashboard (Flask-coreUI)
This application is a results Dashboard for MolSSI projects.

The server runs Flask on Passenger and Apache, or can run flask testing server.

### Run the Development Web Server

Use `conda` to create an environment from the included environment yaml file, then activate the environment.

```
conda env create -f seamm-dashboard.yml
conda activate seamm-dashboard
```

Next, navigate to `app/static` to install the necessary javascript plugins

```
cd app
cd static
npm install
```

You can then run the development dashboard

```
cd ..
cd ..
python results_dahboard.py
```

The dashboard can then be viewed in your browser at `localhost:5000`.

## Connecting to SEAMM Installation

The dashboard is currently set up to run in `development` mode, meaning that it is showing sample data from the directory `data/projects` in this repository. To have it read data from your locally installed version of SEAMM, change the word `development` to `seamm` in `results_dashboard.py` (line 8).
