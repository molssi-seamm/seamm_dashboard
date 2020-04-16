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
python results_dashboard.py
```

The dashboard can then be viewed in your browser at `localhost:5000`.

## Connecting to SEAMM Installation

The dashboard is currently set up to run in `development` mode, meaning that it is showing sample data from the directory `data/projects` in this repository. To have the SEAMM dashboard read data from your locally installed version of SEAMM, follow the instructions in the section above, but change the word `development` to `seamm` in `results_dashboard.py` (line 8). This will read the location of the data store from your `seamm.ini` file.
