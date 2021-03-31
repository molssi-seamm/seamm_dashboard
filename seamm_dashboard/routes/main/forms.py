from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class SoftwareForm(FlaskForm):
    name = StringField("What is your name?")
    domain = StringField("Which domain")
    submit = SubmitField("Submit")
