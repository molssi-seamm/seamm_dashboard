#!/usr/bin/env python
from seamm_dashboard import create_app, options
from waitress import serve


def run():
    app = create_app()

    # serve using waitress
    if "debug" in options:
        app.run(debug=True, use_reloader=True)  
    else:   
        # serve using waitress
        if options["localhost"]:
            serve(app, listen=f"localhost:{options['port']}", threads=12)
        else:
            serve(app, port=options["port"], threads=12)


if __name__ == "__main__":
    run()
