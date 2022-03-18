from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, TextAreaField, SubmitField

from wtforms.validators import DataRequired, Length, Regexp


class EditJob(FlaskForm):
    name = StringField(
        "Job Title",
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_. ]*$",
                0,
                "Job titles must have only letters, numbers, "
                + "dots, spaces, or underscores",
            ),
        ],
    )
    notes = TextAreaField("Description")
    submit = SubmitField("Update Job")


class ImportJob(FlaskForm):
    outfile = FileField("job_data.json File", validators=[DataRequired()])
    title = StringField("Job Title")
    submit = SubmitField("Import Job")
