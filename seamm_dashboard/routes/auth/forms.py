from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField

try:
    from wtforms.fields import EmailField
except ImportError:
    from wtforms.fields.html5 import EmailField

from wtforms.validators import DataRequired, Length, EqualTo, Email

from seamm_dashboard.routes.admin.forms import _validate_email, _password_none_or_usual


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(3, 64)])
    password = PasswordField("Password", validators=[DataRequired()])
    # remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Log In")


class ConfirmLogin(FlaskForm):
    """A login form which doesn't have a username field"""

    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class UpdateAccountInfoForm(FlaskForm):
    """
    A form a user uses to update their own information. Users cannot change their
    username.
    """

    password2 = PasswordField("Confirm password", validators=[_password_none_or_usual])

    password = PasswordField(
        "Password",
        validators=[
            EqualTo("password2", message="Passwords must match."),
        ],
    )

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

    submit = SubmitField("Update User Information")
