"""
Filetrs for Jinia templates
"""

from flask import current_app


def replace_empty(s):
    """Replace empty strings"""

    if not s:
        return current_app.config["REPLACE_NONE"]

    return s
