#!/usr/bin/env python
from app import create_app


def run():
    app = create_app()
    app.run(debug=True, use_reloader=False)


if __name__ == "__main__":
    run()
