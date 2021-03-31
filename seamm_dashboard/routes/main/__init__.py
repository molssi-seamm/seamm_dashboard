from flask import Blueprint

main = Blueprint("main", __name__)

from . import views, errors  # noqa: F401, E402

# from ..models.users import Permission


# @main.app_context_processor
# def inject_permissions():
#     return dict(Permission=Permission)
