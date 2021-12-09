"""
Admin views
"""

from copy import deepcopy

from flask import render_template, redirect, url_for, flash, Response, request

from flask_jwt_extended import (
    jwt_required,
    get_current_user,
)

from .forms import (
    CreateUserForm,
    ManageUserFormAdmin,
    EditGroupForm,
    DeleteUserForm,
    DeleteGroupForm,
    _validate_username,
    _validate_email,
    _validate_group,
    _validate_user_delete,
)

from wtforms import BooleanField

from . import admin

from seamm_dashboard import db, authorize
from seamm_datastore.database.models import (
    Role,
    Group,
    User,
    Project,
    GroupProjectAssociation,
    UserProjectAssociation,
)
from seamm_dashboard.routes.api.users import _process_user_body


def _process_user_permissions(filled_form, user):

    # Empty dictionary containing all entries
    permissions_dict = {
        int(k.split("_")[1]): []
        for k in filled_form.data.keys()
        if "specialproject" in k
    }

    # Get just the checked fields
    specialproject_keys = [
        x
        for x in filled_form.data.keys()
        if "specialproject" in x
        if filled_form.data[x] is True
    ]

    # Loop over checked fields and update dictionary containing all entries.
    # First collect permissions which were set in form
    # Build permissions dictionary (keys are project IDs,
    # values are permissions ("read", "update", etc))
    for key in specialproject_keys:
        split = key.split("_")
        project_id = int(split[1])
        permissions_dict[project_id].append(split[2])

    # Loop through permissions dictionary built in previous loop.
    # This is done after processing permissions because we need a full
    # list of the permissions for updating.
    for project_id, permission in permissions_dict.items():
        project = Project.query.filter_by(id=project_id).one()

        # Look to see if setting exists yet
        assoc = UserProjectAssociation.query.filter_by(
            entity_id=user.id, resource_id=project.id
        ).one_or_none()

        if not assoc:
            assoc = UserProjectAssociation(
                entity_id=user.id, resource_id=project.id, permissions=permission
            )
        else:
            assoc.permissions = permission

        db.session.add(assoc)
        db.session.commit()


def _bind_user_projects_to_form(form, projects, user=None, new=True):

    if not new and not user:
        raise ValueError(
            "A user must be given if the form is being created for an existing user."
        )

    project_names = []
    actions = ["read", "update", "create", "delete", "manage"]

    # Bind boolean fields for permission types
    for project in projects:
        field_name = f"specialproject_{project.id}"
        permissions = []
        if not new:
            assoc = UserProjectAssociation.query.filter_by(
                resource_id=project.id, entity_id=user.id
            ).one_or_none()

            if assoc:
                permissions = assoc.permissions

        for action in actions:
            checked = action in permissions
            setattr(form, f"{field_name}_{action}", BooleanField(default=checked))

        project_names.append({"name": project.name, "id": project.id})

    return form, project_names


def _bind_special_projects_to_form(form, projects, group=None, new=True):

    if not new and not group:
        raise ValueError(
            "A group must be given if the form is being created for an existing group."
        )

    project_names = []
    actions = ["read", "update", "create", "delete", "manage"]

    # Bind boolean fields for permission types
    for project in projects:
        field_name = f"specialproject_{project.id}"
        permissions = []
        if not new:
            assoc = GroupProjectAssociation.query.filter_by(
                resource_id=project.id, entity_id=group.id
            ).one_or_none()

            if assoc:
                permissions = assoc.permissions

        for action in actions:
            checked = action in permissions
            setattr(form, f"{field_name}_{action}", BooleanField(default=checked))

        project_names.append({"name": project.name, "id": project.id})

    return form, project_names


def _bind_owned_projects_to_form(form, projects, group=None, new=True):

    if not new and not group:
        raise ValueError(
            "A group must be given if the form is being created for an existing group."
        )

    project_names = []
    actions = ["read", "update", "create", "delete", "manage"]

    # Bind boolean fields for permission types
    for project in projects:
        field_name = f"ownedproject_{project.id}"
        permissions = project.group_permissions

        for action in actions:
            checked = action in permissions
            setattr(form, f"{field_name}_{action}", BooleanField(default=checked))

        project_names.append({"name": project.name, "id": project.id})

    return form, project_names


def _process_group_form_data(form):

    # Process form data
    # Get users specified on form from db
    users = User.query.filter(User.username.in_(form.data["group_members"])).all()

    group = Group.query.filter_by(name=form.data["group_name"]).one_or_none()

    if group is None:
        # Create new group containing users
        group = Group(name=form.data["group_name"], users=users)
    else:
        group.users = users

    db.session.add(group)
    db.session.commit()

    permissions_dict = {}

    specialproject_keys = [
        x for x in form.data.keys() if "specialproject" in x if form.data[x] is True
    ]

    # First collect permissions which were set in form
    for key in specialproject_keys:
        split = key.split("_")
        project_id = int(split[1])

        try:
            permissions_dict[project_id].append(split[2])
        except KeyError:
            permissions_dict[project_id] = [split[2]]

    for project_id, permission in permissions_dict.items():
        project = Project.query.filter_by(id=project_id).one()

        # Look to see if setting exists yet
        assoc = GroupProjectAssociation.query.filter_by(
            entity_id=group.id, resource_id=project.id
        ).one_or_none()

        if not assoc:
            assoc = GroupProjectAssociation(
                entity_id=group.id, resource_id=project.id, permissions=permission
            )
        else:
            assoc.permissions = permission

        db.session.add(assoc)
        db.session.commit()

    # Set owned project permissions
    owned_projects = Project.query.filter_by(group_id=group.id)
    for project in owned_projects:
        # Zero permissions
        perm = project.permissions
        perm["group"] = []
        project.set_permissions(perm)
        db.session.add(project)
        db.session.commit()

    ownedproject_keys = [
        x for x in form.data.keys() if "ownedproject" in x if form.data[x] is True
    ]

    # Update permissions
    for key in ownedproject_keys:
        split = key.split("_")
        project_id = int(split[1])
        permission = split[2]

        project = Project.query.filter_by(id=project_id).one()
        perm = deepcopy(project.permissions)
        perm["group"].append(permission)
        project.set_permissions(perm)
        db.session.add(project)
        db.session.commit()


@admin.route("/admin/manage_users")
@jwt_required(optional=True)
def manage_users():
    if not authorize.has_role("admin"):
        return render_template("401.html")
    return render_template("admin/manage_users.html")


@admin.route("/admin/manage_groups")
@jwt_required(optional=True)
def manage_groups():
    if not authorize.has_role("admin", "group manager"):
        return render_template("401.html")
    return render_template("admin/manage_groups.html")


@admin.route("/admin/create_group", methods=["GET", "POST"])
@jwt_required(optional=True)
def create_group():
    if not authorize.has_role("admin", "group manager"):
        return render_template("401.html")

    # We have to add these fields dynamically based on the projects in the database
    projects = Project.query.all()

    form_copy = deepcopy(EditGroupForm)
    form_copy, project_names = _bind_special_projects_to_form(form_copy, projects)

    form = form_copy()
    users = User.query.all()
    form.group_members.choices = [(user.username, user.username) for user in users]

    if form.validate_on_submit():

        _process_group_form_data(form)

        flash(f"The group {form.data['group_name']} has been successfully created")
        return render_template("admin/manage_groups.html")

    return render_template(
        "admin/create_group.html", form=form, special_project_names=project_names
    )


@admin.route("/admin/manage_group/<group_id>", methods=["GET", "POST"])
@jwt_required(optional=True)
def manage_group(group_id):
    # Permissions check
    if not authorize.has_role("admin", "group manager"):
        return render_template("401.html")

    # Get the group information
    group = Group.query.get(group_id)

    if not group:
        return render_template("404.html")

    # We have to add project fields dynamically based on the projects in the database

    # Get projects owned by the group
    owned_projects = Project.query.filter_by(group_id=group.id).all()

    # Get all projects in db
    projects = Project.query.all()

    # special projects
    special_projects = list(set(projects) - set(owned_projects))

    form_copy = deepcopy(EditGroupForm)
    form_copy, special_projects = _bind_special_projects_to_form(
        form_copy, special_projects, new=False, group=group
    )
    form_copy, owned_projects = _bind_owned_projects_to_form(
        form_copy, owned_projects, new=False, group=group
    )

    form = form_copy()
    users = User.query.all()
    form.group_members.choices = [(user.username, user.username) for user in users]

    # Set defaults
    if request.method == "GET":
        form.group_name.data = group.name
        form.group_members.data = [g.username for g in group.users]

    if request.method == "POST":
        try:
            form.group_name.validators.remove(_validate_group)
        except ValueError:
            pass

        # field has been attempted to be updated and we
        # must check the input
        if form.group_name.data != group.name:
            if Group.query.filter(Group.name == form.group_name.data).first():
                form.group_name.validators.append(_validate_group)

        # use validate instead of validate_on_submit so we can add our own validators
        # (lines above)
        if form.validate():

            _process_group_form_data(form)

            db.session.commit()
            flash(f"The group {form.data['group_name']} has been successfully updated.")
            return render_template("admin/manage_groups.html")

    return render_template(
        "admin/create_group.html",
        form=form,
        owned_project_names=owned_projects,
        special_project_names=special_projects,
        group_name=group.name,
        group_id=group.id,
    )


@admin.route("/admin/create_user", methods=["GET", "POST"])
@jwt_required(optional=True)
def create_user():

    if not authorize.has_role("admin"):
        return render_template("401.html")

    projects = Project.query.all()

    form = deepcopy(CreateUserForm)
    form, project_names = _bind_user_projects_to_form(form, projects=projects)
    form = form()
    form.groups.choices = [(g.name, g.name) for g in Group.query.all()]
    form.roles.choices = [(r.name, r.name) for r in Role.query.all()]

    if form.validate_on_submit():
        processed_form = _process_user_body(form.data)

        if isinstance(processed_form, Response):
            flash(
                "Creating the user failed because of problems with the input data. "
                "Please check the inputs and try again."
            )
            return redirect(url_for("admin.create_user"))

        else:
            db.session.add(processed_form)
            db.session.commit()

            _process_user_permissions(form, processed_form)

            flash(f"The user {form.data['username']} has been successfully created")
            return render_template("admin/manage_users.html")

    return render_template("admin/create_user.html", form=form, projects=project_names)


@admin.route("/admin/manage_user/<user_id>", methods=["GET", "POST"])
@jwt_required(optional=True)
def manage_user(user_id):

    # Permissions check
    if not authorize.has_role("admin"):
        return render_template("401.html")

    # Get the user information
    user = User.query.get(user_id)

    if not user:
        return render_template("404.html")

    projects = Project.query.all()

    form = deepcopy(ManageUserFormAdmin)
    form, project_names = _bind_user_projects_to_form(
        form, projects=projects, user=user, new=False
    )
    form = form()

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

        # Each of these has to be tried - two separate try statements
        try:
            form.username.validators.remove(_validate_username)
        except ValueError:
            pass

        try:
            form.email.validators.remove(_validate_email)
        except ValueError:
            pass

        # field has been attempted to be updated and we
        # must check the input
        if form.username.data != user.username:
            if User.query.filter(User.username == form.username.data).first():
                form.username.validators.append(_validate_username)

        if form.email.data != user.email:
            if User.query.filter(User.email == form.email.data).first():
                form.email.validators.append(_validate_email)

        # use validate instead of validate_on_submit so we can add our own validators
        # (lines above)
        if form.validate():

            user = _process_user_body(form.data, original_user_data=user)
            db.session.add(user)
            db.session.commit()
            _process_user_permissions(form, user)
            flash(f"The user {form.data['username']} has been successfully updated.")
            return render_template("admin/manage_users.html")

    return render_template(
        "admin/create_user.html",
        form=form,
        username=user.username,
        user_id=user.id,
        projects=project_names,
    )


@admin.route("/admin/manage_user/<user_id>/delete", methods=["GET", "POST"])
@jwt_required(fresh=True)
def delete_user(user_id):
    # Permissions check
    if not authorize.has_role("admin"):
        return render_template("401.html")

    user_remove = User.query.filter(User.id == user_id).one()

    if user_remove.id == get_current_user().id:
        flash("You cannot remove your own account from the dashboard.")
        return render_template("admin/manage_users.html")

    form = DeleteUserForm()

    try:
        form.username.validators.remove(_validate_username)
    except ValueError:
        pass

    if request.method == "POST":

        specified_user = User.query.filter_by(username=form.username.data).one_or_none()

        if specified_user is None or str(specified_user.id) != user_id:
            form.username.validators.append(_validate_user_delete)
            flash("The input username did not match the requested user.")

        if form.validate():
            db.session.delete(specified_user)
            db.session.commit()
            flash(f"User {specified_user.username} removed from the dashboard.")

            return render_template("admin/manage_users.html")

    return render_template("admin/delete_user.html", form=form)


@admin.route("/admin/manage_group/<group_id>/delete", methods=["GET", "POST"])
@jwt_required(fresh=True)
def delete_group(group_id):
    # Permissions check
    if not authorize.has_role("admin", "group manager"):
        return render_template("401.html")

    form = DeleteGroupForm()

    if request.method == "POST":

        specified_group = Group.query.filter_by(name=form.group_name.data).one_or_none()

        if specified_group is None or str(specified_group.id) != group_id:
            form.group_name.validators.append(_validate_user_delete)
            flash("The input group name did not match the requested group.")

        if form.validate():
            db.session.delete(specified_group)
            db.session.commit()
            flash(f"Group {specified_group.name} removed from the dashboard.")

            return render_template("admin/manage_groups.html")

    return render_template("admin/delete_group.html", form=form)
