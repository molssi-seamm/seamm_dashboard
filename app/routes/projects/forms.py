from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired


class EditProject(FlaskForm):
    name = StringField("Project Title")
    notes = TextAreaField("Description")
    submit = SubmitField("Update Project")
