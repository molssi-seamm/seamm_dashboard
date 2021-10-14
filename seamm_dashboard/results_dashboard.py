#!/usr/bin/env python
import sqlalchemy
from seamm_dashboard import create_app
from seamm_dashboard.setup_argparsing import options

from seamm_datastore import connect

def run():
    app = create_app()
    app.run(debug=True, use_reloader=True)


if __name__ == "__main__":
    run()
