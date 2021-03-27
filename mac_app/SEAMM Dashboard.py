#!/usr/bin/env python
from seamm_dashboard import create_app


def run():
    app = create_app()
    app.run(debug=False, use_reloader=False)


if __name__ == "__main__":
    run()
