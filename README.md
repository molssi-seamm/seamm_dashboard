# MolSSI Dashboard (Flask-coreUI)
This application is a results Dashborad for MolSSI projects.

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
