from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField

from wtforms.validators import DataRequired, Length, Regexp


class EditProject(FlaskForm):
    name = StringField(
        "Project Title",
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_. ]*$",
                0,
                "Projects must have only letters, numbers, "
                + "dots, spaces, or underscores",
            ),
        ],
    )
    notes = TextAreaField("Description")
    submit = SubmitField("Update Project")


class AddProject(FlaskForm):
    name = StringField(
        "Project Title",
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_. ]*$",
                0,
                "Projects must have only letters, numbers, "
                + "dots, spaces, or underscores",
            ),
        ],
    )
    notes = TextAreaField("Description")
    submit = SubmitField("Create Project")


class ManageProjectAccessForm(FlaskForm):

    submit = SubmitField("Update Project Access")
