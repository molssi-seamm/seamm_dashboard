"""
Admin views
"""

from flask import render_template, redirect, url_for, flash, Response, request

from flask_jwt_extended import jwt_optional

from .forms import (
    CreateUserForm,
    ManageUserFormAdmin,
    _validate_username,
    _validate_email,
)

from . import admin

from app import db, authorize
from app.models import Role, Group, User
from app.routes.api.users import _process_user_body


@admin.route("/admin/manage_users")
@jwt_optional
def manage_users():
    if not authorize.has_role("admin"):
        return render_template("401.html")
    return render_template("admin/manage_users.html")


@admin.route("/admin/create_user", methods=["GET", "POST"])
@jwt_optional
def create_user():

    if not authorize.has_role("admin"):
        return render_template("401.html")

    form = CreateUserForm(new_user=False)
    form.groups.choices = [(g.name, g.name) for g in Group.query.all()]
    form.roles.choices = [(r.name, r.name) for r in Role.query.all()]

    if form.validate_on_submit():
        processed_form = _process_user_body(form.data)

        if isinstance(processed_form, Response):
            flash(
                f"Creating the user failed because of problems with the input data. Please check the inputs and try again."
            )
            return redirect(url_for("admin.create_user"))

        else:
            db.session.add(processed_form)
            db.session.commit()
            flash(f"The user {form.data['username']} has been successfully created")
            return render_template("admin/manage_users.html")

    return render_template("admin/create_user.html", form=form)


@admin.route("/admin/manage_user/<user_id>", methods=["GET", "POST"])
@jwt_optional
def manage_user(user_id):

    # Permissions check
    if not authorize.has_role("admin"):
        return render_template("401.html")

    # Get the user information
    user = User.query.get(user_id)

    if not user:
        return render_template("404.html")

    form = ManageUserFormAdmin()
    form.groups.choices = [(g.name, g.name) for g in Group.query.all()]
    form.roles.choices = [(r.name, r.name) for r in Role.query.all()]

    # Set defaults based on user
    if request.method == "GET":
        form.username.data = user.username
        form.groups.data = [g.name for g in user.groups]
        form.roles.data = [r.name for r in user.roles]
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.email.data = user.email

    if request.method == "POST":
        try:
            form.username.validators.remove(_validate_username)
            form.email.validators.remove(_validate_email)
        except:
            pass

        # field has been attempted to be updated and we
        # must check the input
        if form.username.data != user.username:
            if User.query.filter(User.username == form.username.data).first():
                form.username.validators.append(_validate_username)

        if form.email.data != user.email:
            if User.query.filter(User.email == form.email.data).first():
                form.email.validators.append(_validate_email)

        # use validate instead of validate_on_submit so we can add our own validators (lines above)
        if form.validate():

            user = _process_user_body(form.data, original_user_data=user)

            db.session.commit()
            flash(f"The user {form.data['username']} has been successfully updated.")
            return render_template("admin/manage_users.html")

    return render_template("admin/create_user.html", form=form, username=user.username)
