#!/usr/bin/env python
from seamm_dashboard import create_app


def run():
    app = create_app()
    # app.run(debug=True, use_reloader=True)
    app.run(debug=True, use_reloader=False, port=6000)


if __name__ == "__main__":
    run()
