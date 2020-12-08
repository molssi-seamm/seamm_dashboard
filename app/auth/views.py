import logging

import json

from flask import (
    render_template,
    redirect,
    request,
    url_for,
    flash,
    jsonify,
    make_response,
    Response
)

# Still importing for un-rewritten routes (leaving for reference)

from flask_jwt_extended import (
    get_jwt_identity,
    jwt_optional,
    jwt_required,
    get_current_user,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)
from ..email import send_email
from .forms import (
    LoginForm,
    CreateUserForm,
    ChangePasswordForm,
    PasswordResetRequestForm,
    PasswordResetForm,
    ChangeEmailForm,
)

from . import auth

from app import db
from app.models import User, UserSchema, Role, Group
from app.routes.api.auth import create_tokens
from app.routes.api.status import status
from app.routes.api.users import _process_user_body


logger = logging.getLogger(__name__)


@auth.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html")


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


@auth.route("/manage_users")
def manage_users():
    return render_template("auth/manage_users.html")


@auth.route("/create_user", methods=["GET", "POST"])
def create_user():

    form = CreateUserForm()
    form.user_groups.choices = [(g.name, g.name) for g in Group.query.all()]
    form.user_roles.choices = [(r.name, r.name) for r in Role.query.all()]

    if form.validate_on_submit():
        processed_form = _process_user_body(form.data)

        if isinstance(processed_form, Response):
            flash(f"Creating the user failed because of problems with the input data. Please check the inputs and try again.")
            return redirect(url_for("auth.create_user"))
        
        else:
            # The re
            db.session.add(processed_form)
            db.session.commit()
            flash(f"The user {form.data['username']} has been created")
            return render_template("auth/manage_users.html")

    return render_template("auth/create_user.html", form=form)
