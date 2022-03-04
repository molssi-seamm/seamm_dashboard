#!/usr/bin/env python
from seamm_dashboard import create_app, options
from waitress import serve


def run():
    app = create_app()
    # app.run(debug=True, use_reloader=True)

    # serve using waitress
    serve(app, port=options["port"])


if __name__ == "__main__":
    run()
