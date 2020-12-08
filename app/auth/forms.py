from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    SelectMultipleField,
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, Email
from wtforms import ValidationError
from app.models import User

from app import db


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(3, 64)])
    password = PasswordField("Password", validators=[DataRequired()])
    # remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Log In")


class CreateUserForm(FlaskForm):
    def validate_email(self, field):
        if User.query.filter(User.email == field.data).first():
            raise ValidationError(f"Email ({field.data}) already registered. ")

    def validate_username(self, field):
        if User.query.filter(User.username == field.data).first():
            raise ValidationError(
                f"Username {field.data} already in use. Please pick a different username"
            )

    username = StringField(
        "Username",
        validators=[
            validate_username,
            DataRequired(),
            Length(3, 64),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Usernames must have only letters, numbers, dots or " "underscores",
            ),
        ],
    )

    first_name = StringField("First Name", validators=[Length(3, 64)])

    last_name = StringField("Last Name", validators=[Length(3, 64)])

    email = EmailField(
        "Email Address",
        validators=[
            DataRequired(),
            Email(),
        ],
    )

    user_roles = SelectMultipleField("User Roles", choices=[])

    user_groups = SelectMultipleField("User Groups", choices=[])

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=7),
            EqualTo("password2", message="Passwords must match."),
        ],
    )
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Create New User")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Old password", validators=[DataRequired()])
    password = PasswordField(
        "New password",
        validators=[
            DataRequired(),
            Length(min=7),
            EqualTo("password2", message="Passwords must match."),
        ],
    )
    password2 = PasswordField("Confirm new password", validators=[DataRequired()])
    submit = SubmitField("Update Password")


class PasswordResetRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(3, 64), Email()])
    submit = SubmitField("Reset Password")


class PasswordResetForm(FlaskForm):
    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="Passwords must match"),
        ],
    )
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Reset Password")


class ChangeEmailForm(FlaskForm):
    email = StringField(
        "New Email", validators=[DataRequired(), Length(3, 64), Email()]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Update Email Address")

    def validate_email(self, field):
        if User.objects(email=field.data).first():
            raise ValidationError("Email already registered.")
