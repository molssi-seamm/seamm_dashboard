# MolSSI Dashboard (Flask-coreUI)
This application is a results Dashboard for MolSSI projects.

The server runs Flask on Passenger and Apache, or can run flask testing server.

### Install the SEAMM dashboard

First, use `conda` to create an environment from the included environment yaml file, then activate the environment.

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

## Running the dashboard

You can then run the development after you have installed and activated the dashboard environment. In the top level of the repository, type the following command into the terminal:

```
results_dashboard.py
```

The dashboard can then be viewed in your browser at `localhost:5000`. By default, the dashboard uses the location of the datastore in ~/.seamm/seamm.ini to locate the datastore to display. This can, however, be overridden by a command line argument `--datastore xxxx`. There are other options available. For more information run

```
results_dashboard.py --help

usage: results_dashboard.py [-h] [--dashboard-configfile DASHBOARD_CONFIGFILE] [--datastore DATASTORE] [--initialize] [--no-check]
                            [--log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}] [--console-log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}] [--log_dir LOG_DIR]
...
optional arguments:
  -h, --help            show this help message and exit
  --dashboard-configfile DASHBOARD_CONFIGFILE
                        a configuration file to override others (default: None)
  --datastore DATASTORE
                        The datastore (directory). [env var: SEAMM_DATASTORE] (default: .)
  --initialize          initialize, or reinitialize, from the job files [env var: INITIALIZE] (default: False)
  --no-check            do not check that jobs are in the database [env var: NO_CHECK] (default: False)
  --log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}
                        the logging level for the dashboard [env var: LOG_LEVEL] (default: INFO)
...
```

By default, if the database does not exist, it will be initialized from the job files in the datastore. Otherwise, the dashboard will scan the job files on startup and add any missing ones to the database. You can prevent this initial check with `--nocheck`. Similarly, if you wish to force the database to be recreated from scratch, use the `--initialize` flag.

## Connecting to the development test datastore

For development it is convenient to use the sample data from the directory `data/` in this repository. To do so, use the `--datastore` option to point to the local directory:

```
results_dashboard --datastore <path>/data
```

At the moment you need to use the full, not relative path. To use an SQLite database in memory use

```
results_dashboard.py --datastore <path>/data --sqlalchemy-database-uri 'sqlite:///:memory:'
```

You might also wish to add `--env development` to activate debugging, etc.
