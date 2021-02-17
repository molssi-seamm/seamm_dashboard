from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired


class EditJob(FlaskForm):
    name = StringField("Job Title")
    notes = TextAreaField("Description")
    submit = SubmitField("Update Job")
