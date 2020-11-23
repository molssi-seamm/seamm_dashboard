import logging

from flask import (
    render_template,
    redirect,
    request,
    url_for,
    flash,
    jsonify,
    make_response,
)

# Still importing for un-rewritten routes (leaving for reference)

from flask_jwt_extended import (
    get_jwt_identity,
    jwt_optional,
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
from app.models import User
from app.routes.api.auth import create_tokens


logger = logging.getLogger(__name__)


@auth.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html")


@jwt_optional
@auth.route("/login", methods=["GET", "POST"])
def login():

    # If current user is logged in, redirect them to the main page.
    if get_current_user():
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one_or_none()

        if user is not None and user.verify_password(form.password.data):
            # redirect to blank login page which will set local storage to
            # reload all tabs (as logged in user)
            response = make_response(render_template("login.html"))

            # Add cookies to response
            access_token, refresh_token = create_tokens(user)
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)

            return response
        flash("Invalid username or password.")

    return render_template("auth/login.html", form=form, current_user=get_current_user)


# Login required.
@auth.route("/logout")
def logout():
    """
    Direct to blank page which sets local storage to log out all other tabs and redirects to main
    """
    response = make_response(render_template("logout.html"))
    unset_jwt_cookies(response)
    return response


@auth.route("/create_user", methods=["GET", "POST"])
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data)
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        # token = user.generate_confirmation_token()
        # send_email(user.email, 'SEAMM Dashboard - Confirm Your Account',
        #           'auth/email/confirm', user=user, token=token)
        flash(f"The user {user.username} has been created")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)

