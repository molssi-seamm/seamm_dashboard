from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, TextAreaField, SubmitField

from wtforms.validators import DataRequired


class EditJob(FlaskForm):
    name = StringField("Job Title")
    notes = TextAreaField("Description")
    submit = SubmitField("Update Job")


class ImportJob(FlaskForm):
    outfile = FileField("job_data.json File", validators=[DataRequired()])
    title = StringField("Job Title")
    submit = SubmitField("Import Job")
