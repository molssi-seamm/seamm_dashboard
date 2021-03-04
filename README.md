# MolSSI Dashboard (Flask-coreUI)
This application is a results Dashboard for MolSSI projects.

The server runs Flask on Passenger and Apache, or can run flask testing server.

### Install the SEAMM dashboard

This repository has a Makefile included to help install the SEAMM dashboard. First, you must create the `conda` environment and install the necessary Javascript packages.

To create the seamm dashboard environment and install the necessary packages, type

~~~bash
$ make environment
~~~

in the top level of your directory.

After the script is finished running, activate the seamm dashboard conda environment:

~~~
conda activate seamm-dashboard
~~~

If your conda environment is activated, you're ready to start running the dashboard.

## Running the dashboard

You can then run the dashboard after you have installed and activated the dashboard environment. 

### Run a demo dashboard

If you do not have SEAMM installed, you can view a demo dashboard by using the data in this repository. Use the command

```
./results_dashboard.py --initialize --datastore $(pwd)/data --jwt-secret-key 'super-secret' --secret-key 'another-super-secret'
```

If you are running the dashboard in production, you should use better secrets.

Open a browser and navigate to `http://localhost:5000/` to  view the sample dashboard. 

### Running with SEAMM installed

If you have SEAMM installed, you can connect to your seamm datastore. In the top level of the repository, type the following command into the terminal:

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
