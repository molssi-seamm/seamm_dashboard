#!/usr/bin/env python
from seamm_dashboard import create_app, options
from waitress import serve

production = False


def run():
    app = create_app()
    # app.run(debug=True, use_reloader=True)

    # serve using waitress
    if production:
        serve(app, port=options["port"], threads=12)
    else:
        serve(app, listen=f"localhost:{options['port']}", threads=12)


if __name__ == "__main__":
    run()
