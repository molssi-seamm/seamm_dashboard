from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField

from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(3, 64)])
    password = PasswordField("Password", validators=[DataRequired()])
    # remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Log In")
