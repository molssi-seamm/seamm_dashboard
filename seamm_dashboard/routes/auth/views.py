import logging

from flask import render_template, flash, make_response, request, redirect, url_for

from flask_jwt_extended import (
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    create_access_token,
    get_current_user,
    jwt_required,
)

from .forms import LoginForm, ConfirmLogin, UpdateAccountInfoForm

from seamm_dashboard import authorize, db
from seamm_datastore.database.models import User, UserProjectAssociation
from seamm_datastore.database.schema import UserSchema

from . import auth

from seamm_dashboard import jwt
from seamm_dashboard.routes.api.auth import create_tokens

from seamm_dashboard.routes.admin.forms import _validate_email
from seamm_dashboard.routes.admin.views import _bind_user_projects_to_form

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


@jwt.needs_fresh_token_loader
@jwt_required(optional=True)
@auth.route("/confirm_login", methods=["GET", "POST"])
def fresh_login(jwt_header, jwt_payload):

    form = ConfirmLogin()
    user = get_current_user()

    if form.validate_on_submit():

        if user.verify_password(form.password.data):
            user_schema = UserSchema(many=False)
            user = user_schema.dump(user)
            response = redirect(request.referrer)

            # Add cookies to response
            access_token = create_access_token(identity=user, fresh=True)
            set_access_cookies(response, access_token)

            return response
        flash("Invalid username or password.")

    return render_template("auth/confirm_login.html", form=form)


@auth.route("/my-account", methods=["GET", "POST"])
@jwt_required(optional=True, fresh=True)
def my_account():

    current_user = get_current_user()

    # Redirect to admin version if logged in user is admin
    if authorize.has_role("admin"):
        return redirect(url_for("admin.manage_user", user_id=current_user.id))

    if current_user is None:
        return redirect(url_for("auth.login"))

    project_association = UserProjectAssociation.query.filter_by(
        entity_id=current_user.id
    ).all()

    projects = []
    if project_association:
        projects = [x.projects for x in project_association]

    form = UpdateAccountInfoForm
    form, project_names = _bind_user_projects_to_form(
        form, projects, user=current_user, new=False
    )

    form = form()

    if request.method == "GET":
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email

    if request.method == "POST":

        try:
            form.email.validators.remove(_validate_email)
        except ValueError:
            pass

        if form.validate():
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.email = form.email.data

            if form.password:
                current_user.password = form.password.data

            db.session.add(current_user)
            db.session.commit()

            flash("Your account has been updated.")

            return redirect(url_for("main.index"))

    return render_template(
        "auth/manage_account.html", form=form, user=current_user, projects=project_names
    )


# Login required.
@auth.route("/logout")
def logout():
    """
    Direct to blank page which sets local storage to log out all other tabs and
    redirects to main
    """
    flash("You have been logged out.")
    response = make_response(render_template("logout.html"))
    unset_jwt_cookies(response)
    return response
