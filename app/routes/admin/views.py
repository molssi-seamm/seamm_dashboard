"""
Admin views
"""

import logging

import json

from flask import render_template, redirect, url_for, flash, make_response, Response

from .forms import (
    CreateUserForm,
)

from . import admin

from app import db
from app.models import User, UserSchema, Role, Group
from app.routes.api.users import _process_user_body


@admin.route("/admin/manage_users")
def manage_users():
    return render_template("admin/manage_users.html")


@admin.route("/admin/create_user", methods=["GET", "POST"])
def create_user():

    form = CreateUserForm()
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
            flash(f"The user {form.data['username']} has been created")
            return render_template("admin/manage_users.html")

    return render_template("admin/create_user.html", form=form)
