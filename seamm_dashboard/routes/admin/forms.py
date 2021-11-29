from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    SelectMultipleField,
    BooleanField,
)

try:
    from wtforms.fields import EmailField
except ImportError:
    from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from seamm_datastore.database.models import User, Group


def _validate_group(self, field):
    if Group.query.filter(Group.name == field.data).first():
        raise ValidationError(
            f"Group name '{field.data}' already in use. Please pick a different group "
            "name."
        )


def _validate_user_delete(self, field):
    raise ValidationError("Input username does not match user ID.")


def _validate_group_delete(self, field):
    raise ValidationError("Input group name does not match group ID.")


def _validate_username(self, field):
    if User.query.filter(User.username == field.data).first():
        raise ValidationError(
            f"Username {field.data} already in use. Please pick a different username"
        )


def _validate_email(self, field):
    if User.query.filter(User.email == field.data).first():
        raise ValidationError(
            f"Email address {field.data} already in use. Please pick a different email "
            "address."
        )


def _password_none_or_usual(self, field):
    """
    This validator is for the manage user form. Either the password is not changed
    (len 0), or the password is changed and should meet the usual length requirement.
    """
    if 0 < len(field.data) < 7:
        raise ValidationError("Passwords must be at least 7 characters in length.")


# Common username field
_username = StringField(
    "Username",
    validators=[
        _validate_username,
        DataRequired(),
        Length(3, 64),
        Regexp(
            "^[A-Za-z][A-Za-z0-9_.]*$",
            0,
            "Usernames must have only letters, numbers, dots or " "underscores",
        ),
    ],
)


class CreateUsernamePasswordForm(FlaskForm):
    """
    A subform for creating a new username and password.
    """

    username = _username

    password2 = PasswordField("Confirm password", validators=[DataRequired()])

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=7),
            EqualTo("password2", message="Passwords must match."),
        ],
    )


class EditUsernamePasswordForm(FlaskForm):
    """
    A subform for editing username and password.
    """

    username = _username

    password = PasswordField(
        "Password",
        validators=[
            _password_none_or_usual,
            EqualTo("password2", message="Passwords must match."),
        ],
    )

    password2 = PasswordField("Confirm Password")


class ContactInformationForm(FlaskForm):
    """
    A form for adding or updating contact information.
    """

    first_name = StringField("First Name", validators=[Length(2, 64)])

    last_name = StringField("Last Name", validators=[Length(2, 64)])

    email = EmailField(
        "Email Address",
        validators=[
            DataRequired(),
            Email(),
            _validate_email,
        ],
    )


class CreateUserForm(CreateUsernamePasswordForm, ContactInformationForm):
    """
    Form for adding or updating a user
    """

    roles = SelectMultipleField("User Roles", choices=[])

    groups = SelectMultipleField("User Groups", choices=[])

    submit = SubmitField("Create New User")


class ManageUserFormAdmin(EditUsernamePasswordForm, ContactInformationForm):
    """
    Form for adding or updating a user
    """

    roles = SelectMultipleField("User Roles", choices=[])

    groups = SelectMultipleField("User Groups", choices=[])

    submit = SubmitField("Update User Information")


class EditGroupForm(FlaskForm):
    """
    Form for adding or editing a group
    """

    group_name = StringField(
        "Group Name", validators=[Length(2, 64), DataRequired(), _validate_group]
    )

    group_members = SelectMultipleField("Group Members", choices=[])

    submit = SubmitField("Submit")


class DeleteUserForm(FlaskForm):
    """
    Form for deleting a user.
    """

    username = _username
    confirm = BooleanField("Confirm")
    submit = SubmitField("Delete User")


class DeleteGroupForm(FlaskForm):
    """
    Form for deleting a user.
    """

    group_name = StringField("Group Name", validators=[Length(2, 64), DataRequired()])
    confirm = BooleanField("Confirm")
    submit = SubmitField("Delete Group")
