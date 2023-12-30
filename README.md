# MolSSI Dashboard (Flask-coreUI)
This application is a results Dashboard for the [SEAMM](https://molssi-seamm.github.io/) project. It is built using the [Flask](https://flask.palletsprojects.com/en/1.1.x/) web framework and the [CoreUI](https://coreui.io/) template. The dashboard is designed to be used with the [SEAMM Datastore](https://github.com/molssi-seamm/seamm_datastore).

## Install the SEAMM dashboard

To install the SEAMM dashboard, it is recommended that you it install it, along with SEAMM using the [installation instructions](https://molssi-seamm.github.io/getting_started/installation/index.html).

The SEAMM installation tutorial will walk you through installing and running the SEAMM dashboard. If you are interested in developing the SEAMM dashboard, you can install it from this repository using the directions below.

## Development Install from this Repository

To install the dashboard for development, you should first fork this repository to your own GitHub account. Then clone the forked repository to your computer. For example, if you are using SSH, type

~~~bash
git clone git@github.com/YOUR_FORK/seamm_dashboard.git
cd seamm_dashboard
~~~

To create the `seamm-dashboard` environment and install the necessary packages, type

~~~bash
make environment
~~~

in the top level of your directory.

After the script is finished running, activate the SEAMM Dashboard conda environment:

~~~bash
conda activate seamm-dashboard
~~~

Next, do a development install of the package:

~~~bash
make dev-install
~~~

## Installing the Datastore (Required)

For a development install, you must all install the SEAMM Datastore.

You must also install the [SEAMM Datastore](https://github.com/molssi-seamm/seamm_datastore). This is the package that manages the database connection. If you are developing for SEAMM, you might find it useful to install the SEAMM Datastore in development mode. To do this, clone the repository and install it in development mode:

~~~bash
git clone https://github.com/molssi-seamm/seamm_datastore.git
cd seamm_datstore
pip install -e .
~~~

### Run a demo dashboard

If you do not have SEAMM installed, you can view a demo dashboard by using the data in this repository. Use the command

```bash
make run-demo
```

Open a browser and navigate to `http://localhost:5505/` to  view the sample dashboard. Running the sample dashboard will create a user in the database with the same username you use on your computer the default password is `default`.

If you would like to run the same demo dashboard in development/debug mode, use the command

```bash
make run-dev
```

This will run the demo dashboard in debug mode, which will allow you to make changes to the code and see the changes reflected in the dashboard. Note that the dashboard will restart when you make changes to the code. 
The development dashboard will be available at `http://localhost:5000/`.

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