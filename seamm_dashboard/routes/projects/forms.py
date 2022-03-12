from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField


class EditProject(FlaskForm):
    name = StringField("Project Title")
    notes = TextAreaField("Description")
    submit = SubmitField("Update Project")


class AddProject(FlaskForm):
    name = StringField("Project Title")
    notes = TextAreaField("Description")
    submit = SubmitField("Create Project")


class ManageProjectAccessForm(FlaskForm):

    submit = SubmitField("Update Project Access")
