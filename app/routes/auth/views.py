import logging

from flask import (
    render_template,
    redirect,
    flash,
    make_response,
)

from flask_jwt_extended import (
    get_current_user,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)

from .forms import (
    LoginForm,
)

from . import auth

from app.models import User
from app.routes.api.auth import create_tokens
from app.routes.api.users import _process_user_body

logger = logging.getLogger(__name__)


@auth.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one_or_none()

        if user is not None and user.verify_password(form.password.data):
            # redirect to blank login page which will set local storage to
            # reload all tabs (as logged in user)
            response = make_response(render_template("login_script.html"))

            # Add cookies to response
            access_token, refresh_token = create_tokens(user)
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)

            return response
        flash("Invalid username or password.")

    return render_template("auth/login.html", form=form)


# Login required.
@auth.route("/logout")
def logout():
    """
    Direct to blank page which sets local storage to log out all other tabs and redirects to main
    """
    flash("You have been logged out.")
    response = make_response(render_template("logout.html"))
    unset_jwt_cookies(response)
    return response
