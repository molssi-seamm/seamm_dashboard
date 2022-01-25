#!/usr/bin/env python
from seamm_dashboard import create_app, options


def run():
    app = create_app()
    # app.run(debug=True, use_reloader=True)
    app.run(debug=False, use_reloader=False, port=options["port"])


if __name__ == "__main__":
    run()
