from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField


class EditJob(FlaskForm):
    name = StringField("Job Title")
    notes = TextAreaField("Description")
    submit = SubmitField("Update Job")
